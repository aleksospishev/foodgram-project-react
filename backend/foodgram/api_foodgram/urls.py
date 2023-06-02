from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api_foodgram.views import (  # SubscribeViewSet, SubscriptionsViewSet,
    IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet)

recipe_router = DefaultRouter()

recipe_router.register('recipes', RecipeViewSet, basename='recipes')
recipe_router.register('ingredients', IngredientViewSet)
recipe_router.register('tags', TagViewSet)
recipe_router.register('users', UserViewSet)


urlpatterns = [
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(recipe_router.urls)),
    path('', include('djoser.urls')),
]
