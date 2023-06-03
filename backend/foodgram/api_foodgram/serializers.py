import base64
import uuid

from api_foodgram.models import (Basket, FavoriteRecipe, Ingredient,
                                 IngredientsRecipe, Recipe, Tag)
from django.core.files.base import ContentFile
from rest_framework import serializers
from users.models import Subscribe
from users.serializers import CustomUserSerializer


class ImageSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            return ContentFile(
                base64.b64decode(imgstr), name=uuid.uuid4().hex + "." + ext
            )
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        read_only_fields = '__all__',


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """
    для модели IngredientsRecipe
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientsRecipeSerializer(many=True,
                                              source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name', 'text',
            'tags', 'image',
            'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Basket.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    image = ImageSerializer()

    class Meta:
        fields = (
            'ingredients',
            'name',
            'cooking_time',
            'image',
            'tags',
            'text',
            'author'
        )
        model = Recipe

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'выберите ингредиенты'}
            )
        ingredient_part = []
        for ingred in ingredients:
            if ingred in ingredient_part:
                raise serializers.ValidationError(
                    {'ingredients': 'данный ингредиен уже добавлен рецепт'}
                )
            ingredient_part.append(ingred)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Необходимо выбрать хотябы один тег'})
        tags_part = []
        for tag in tags:
            if tag in tags_part:
                raise serializers.ValidationError(
                    {'tags': 'этот тег уже добавлен'})
            tags_part.append(tag)
        return value

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientsRecipeSerializer(
            instance.recipe_ingredients.all(), many=True).data
        return ingredients

    def tags_ingredients_create(self, ingredients, tags, model):
        for ingry in ingredients:
            IngredientsRecipe.objects.update_or_create(
                recipe=model,
                ingredient=ingry['id'],
                amount=ingry['amount'])
        model.tags.set(tags)

    def create(self, validated_data):
        data_ingredients = validated_data.pop('ingredients')
        data_tags_id = validated_data.pop('tags')
        recipe_create = Recipe.objects.create(**validated_data)
        self.tags_ingredients_create(data_ingredients,
                                     data_tags_id, recipe_create)
        return recipe_create

    def update(self, instance, validated_data):
        data_ingredients = validated_data.pop('ingredients')
        data_tags_id = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.tags_ingredients_create(data_ingredients, data_tags_id, instance)
        return super().update(instance, validated_data)


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=obj,
                                        author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeHelpSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def create(self, validated_data):
        author = validated_data.pop('author')
        user = validated_data.pop('user')
        subscribe = Subscribe.objects.create(author='author', user='user')
        return subscribe

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context.get('author')
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на автора {author}.')
        return data
