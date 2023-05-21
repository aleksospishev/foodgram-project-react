from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api_foodgram.views import (IngredientViewSet, RecipeViewSet,
                                SubscribeViewSet, SubscriptionsViewSet,
                                TagViewSet)

recipe_router = DefaultRouter()

recipe_router.register('recipes', RecipeViewSet, basename='recipes')
recipe_router.register('ingredients', IngredientViewSet)
recipe_router.register('tags', TagViewSet)
recipe_router.register(
    'users/subscriptions',
    SubscriptionsViewSet,
    basename='subscriptions'
)
recipe_router.register(
    r'users/(?P<user_id>[\d]+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)


urlpatterns = [
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(recipe_router.urls)),
    path('', include('djoser.urls')),
]
