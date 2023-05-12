import base64

# from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import Subscribe, User
from users.serializers import CustomUserSerializer

from api_foodgram.models import (Basket, Comment, FavoriteRecipe, Ingredient,
                     IngredientsRecipe, Recipe, Review, Tag, TagsRecipe)


class ImageSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
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
            'measurement_unit',
            'text'
        )


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredient')
    # name = serializers.CharField(source='ingredient.name')
    # quantity = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsRecipe
        fields = (
            'id',
            # 'name',
            # 'quantity'
            'amount'
        )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        if data['amount'] <= 0:
            raise serializers.ValidationError(
                'кол-во ингредиентов должно быть больше нуля'
            )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    # review_author\
    # review_author = ReviewAuthorSerializer()
    ingredients = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    in_basket = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name', 'text',
            'tags', 'image',
            # 'review_author',
            'cooking_time',
            'favorite', 'in_basket'
        )

    def get_ingredients(self, obj):
        amount_ingrs = IngredientsRecipe.objects.filter(recipe=obj)
        serializer = IngredientCreateSerializer(amount_ingrs, many=True)
        return serializer.data

    def get_favorite(self, obj):
        request = self.context.get('request', )
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_in_basket(self, obj):
        request = self.context.get('request', )
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
    review_author = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=False
    )
    image = ImageSerializer(required=False)

    class Meta:
        fields = (
            'ingredients',
            'name',
            'cooking_time',
            'image',
            'review_author',
            'tags',
            'text'
        )
        model = Recipe

    def create_tag_ingredient(self, data_ingredients,
                              data_tags_id, recipe_create
                              ):
        tag_objs = [
            TagsRecipe(recipe=recipe_create, tag=tag_id)
            for tag_id in data_tags_id
        ]
        TagsRecipe.objects.bulk_create(tag_objs)
        ingredient_part = []
        for ingred in data_ingredients:
            ingr = get_object_or_404(Ingredient, id=ingred['ingredient'])
            amount = ingred['amount']
            ingredient_part.append(
                IngredientsRecipe(
                    recipe=recipe_create,
                    ingredient=ingr,
                    amount=amount
                )
            )
        IngredientsRecipe.objects.bulk_create(ingredient_part)

    def create(self, validated_data):
        data_ingredients = validated_data.pop('ingredients')
        data_tag = validated_data.pop('tags')
        # data_review = validated_data.pop('review_author')
        recipe_create = Recipe.objects.create(**validated_data)
        self.create_tag_ingredient(
             data_ingredients, data_tag, recipe_create,)
        return recipe_create

    def update(self, instance, validated_data):
        data_ingredients = validated_data.pop('ingredients')
        data_tag = validated_data.pop('tags')
        # data_review = validated_data.pop('review_author')
        TagsRecipe.objects.filter(recipe=instance).delete()
        IngredientsRecipe.objects.filter(recipe=instance).delete()
        # Recipe.objects.filter(recipe=instance)
        self.create_tag_ingredient(data_ingredients, data_tag, instance)
        return super().update(instance, validated_data)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        if not data['ingredients']:
            raise serializers.ValidationError(
                detail='рецепт должен содержать ингредиенты'
            )
        if not data['tags']:
            raise serializers.ValidationError(
                detail='рецепт должен содержать тэг'
            )
        if data['cooking_time'] < 0:
            raise serializers.ValidationError(
                detail='Время приготовления больше нуля!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'comment'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False,
    )
    review = serializers.IntegerField(
        min_value=1,
        max_value=5
    )
    tasty_review = serializers.IntegerField(
        min_value=1,
        max_value=5
    )
    cooking_review = serializers.IntegerField(
        min_value=1,
        max_value=5
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'author',
            'review',
            'cooking_review',
            'tasty_review'
        )

    def validate(self, data):
        recipe_id = self.context['recipe.id']
        review_exists = Review.objects.filter(
            author=self.context['request'].user,
            recipe=recie_id
        ).count()
        recipe = get_object_or_404(
            Recipe,
            id=recipe_id
        )
        if not request or request.user.is_anonymous:
            return False
        if self.context['request'].method == 'POST' and review_exists:
            raise serializers.ValidationError(
                f'Отзыв на {recipe.name} уже существует'
            )
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request', )
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user,
            is_subscribed=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def create(self, validated_data):
        author_subs = get_object_or_404(
            User,
            id=self.context['request'].parser_context['kwargs']['user_id']
        )
        Subscribe.objects.create(
            user=self.context['request'].user,
            is_subscribed=author_subs
        )
        return author_subs

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        subs_id = self.context['request'].parser_context['kwargs']['user_id']
        subs = get_object_or_404(User, id=subs_id)
        user = self.context['request'].user
        if user == subs:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Subscribe.objects.filter(user=user, is_subscribed=subs).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на автора {subs}.'
            )
        return data


class RecipeHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class BasketSerializer(RecipeHelpSerializer):
    def create(self, validated_data):
        recipe_basket = get_object_or_404(
            Recipe,
            id=self.context['request'].parser_context['kwargs']['recipe_id']
        )
        Basket.objects.create(
            user=self.context['request'].user,
            recipe=recipe_basket
        )
        return recipe_basket

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        recipe = self.context['request'].parser_context['kwargs']['recipe_id']
        user = self.context['request'].user
        if Basket.objects.filter(user=user, recipe=recipe).exists():
            recipe_name = Recipe.objects.get(id=recipe).name
            raise serializers.ValidationError(
                f'Рецепт ({recipe_name}) уже добавлен в Ваш список покупок.'
            )
        return data


class FavoriteRecipeSerializer(RecipeHelpSerializer):
    def create(self, validated_data):
        recipe_favorite = get_object_or_404(
            Recipe,
            id=self.context['request'].parser_context['kwargs']['recipe_id']
        )
        FavoriteRecipe.objects.create(
            user=self.context['request'].user,
            recipe=recipe_favorite
        )
        return recipe_favorite

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        recipe = self.context['request'].parser_context['kwargs']['recipe_id']
        user = self.context['request'].user
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            recipe_name = Recipe.objects.get(id=recipe).name
            raise serializers.ValidationError(
                f'Рецепт ({recipe_name}) уже добавлен в Ваш список избранного.'
            )
        return data
