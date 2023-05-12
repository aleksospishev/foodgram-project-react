from djoser import serializers
from rest_framework.serializers import SerializerMethodField

from users.models import Subscribe, User


class CustomUserSerializer(serializers.UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request',)
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user,
            is_subscribed=obj
        ).exists()
