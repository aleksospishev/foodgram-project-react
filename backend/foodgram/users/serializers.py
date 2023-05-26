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

