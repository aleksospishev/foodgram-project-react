import base64
import uuid

from api_foodgram.models import (Basket, FavoriteRecipe, Ingredient,
                                 IngredientsRecipe, Recipe, Tag)
from django.core.files.base import ContentFile
from rest_framework import serializers, status
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
            'measurement_unit'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsRecipe
        fields = ('id',
                  'amount'
                  )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientsRecipeSerializer(many=True)
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


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    image = ImageSerializer()

    class Meta:
        fields = (
            'ingredients',
            'name',
            'cooking_time',
            'image',
            'tags',
            'text'
        )
        model = Recipe

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'выберите ингредиенты'},
                status.HTTP_400_BAD_REQUEST
            )
        ingredient_part = []
        for ingred in ingredients:
            if ingred in ingredient_part:
                raise serializers.ValidationError(
                    {'ingredients': 'данный ингредиен уже добавлен рецепт'},
                    status.HTTP_400_BAD_REQUEST
                )
            ingredient_part.append(ingred)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Необходимо выбрать хотябы один тег'},
                status.HTTP_400_BAD_REQUEST)
        tags_part = []
        for tag in tags:
            if tag in tags_part:
                raise serializers.ValidationError(
                    {'tags': 'этот тег уже добавлен'},
                    status.HTTP_400_BAD_REQUEST)
            tags_part.append(tag)
        return value

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientsRecipeSerializer(
            instance.recipe_ingredients.all(), many=True).data
        return ingredients

    def tags_ingredients_create(self, ingredients, tags, model):
        for ingredient in ingredients:
            IngredientsRecipe.objects.update_or_create(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
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
        self.tags_ingredients_create(data_ingredients, data_tags_id, instance)
        return super().update(instance, validated_data)


class RecipeHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class BasketSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )

    class Meta:
        model = Basket
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')
