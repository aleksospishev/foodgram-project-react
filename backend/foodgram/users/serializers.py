from api_foodgram.serializers import RecipeHelpSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from users.models import Subscribe, User


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
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
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user,
            author=obj
        ).exists()

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

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        subs_id = self.context['request'].parser_context['kwargs']['user_id']
        subs = get_object_or_404(User, id=subs_id)
        user = self.context['request'].user
        if user == subs:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя',
                status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(user=user, is_subscribed=subs).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на автора {subs}.',
                status.HTTP_400_BAD_REQUEST
            )
        return data
