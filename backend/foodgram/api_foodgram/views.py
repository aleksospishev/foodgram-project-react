from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User, Subscribe

from api_foodgram.filters import IngredientSearchFilter, RecipeFilter
from api_foodgram.models import (Basket, FavoriteRecipe, Ingredient,
                                 Recipe, Tag)
from api_foodgram.pagination import PagePagination
from api_foodgram.permissions import (AuthorOnly, AuthorAdminOrReadOnly,
                         SubscribeUser)
from api_foodgram.serializers import (BasketSerializer,
                         FavoriteRecipeSerializer, IngredientSerializer,
                         RecipeCreateSerializer, RecipeSerializer,
                         TagSerializer)
from users.serializers import SubscribeSerializer
from api_foodgram.utils import get_basket


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    pagination_class = PagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        in_basket = self.request.query_params.get('is_in_shopping_cart')
        if is_favorited is not None and int(is_favorited) == 1:
            favorites = FavoriteRecipe.objects.all().values_list(
                'recipe', flat=True
            )
            return queryset.filter(id__in=favorites)
        if in_basket is not None and int(is_in_cart) == 1:
            in_basket = Basket.objects.all().values_list(
                'recipe', flat=True
            )
            return queryset.filter(id__in=in_basket)
        return queryset

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = RecipeSerializer(
            instance=serializer.instance
        )
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(instance=recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = RecipeSerializer(
            instance=serializer.instance
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        return get_basket(self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filteset_class = IngredientSearchFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class ListModelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class SubscriptionsViewSet(ListModelViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = PagePagination
    permission_classes = (SubscribeUser,)

    def get_queryset(self):
        subscriptions_queryset = self.request.user.subscriber.all()
        subscriptions_list = subscriptions_queryset.values_list(
            'is_subscribed', flat=True
        )
        return User.objects.filter(id__in=subscriptions_list)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (SubscribeUser,)

    def get_queryset(self):
        return self.get_object_or_404(User, id=self.kwargs.get('user_id'))

    def delete(self, request, user_id, format=None):
        unsubs = get_object_or_404(User, id=user_id)
        try:
            subscribe = get_object_or_404(
                Subscribe,
                user=self.request.user,
                is_subscribed=unsub
            )
        except status.HTTP_404_NOT_FOUND:
            message = f'Автор {unsubs} отсутствут в Ваших подписках.'
            return Response(
                {'errors': message}, status.HTTP_400_BAD_REQUEST
            )
        subscribe.delete()
        return Response(status.HTTP_204_NO_CONTENT)


class BasketViewSet(viewsets.ModelViewSet):
    serializer_class = BasketSerializer
    permission_classes = (AuthorOnly,)

    def get_queryset(self):
        return get_object_or_404(
            Recipe, id=self.kwargs.get('recipe.id')
        )

    def delete(self, request, recipe_id, format=None):
        recipe_basket = get_object_or_404(
            Recipe, id=recipe_id
        )
        try:
            items = get_object_or_404(
                Basket, user=self.request.user,
                recipe=recipe_basket
            )
        except status.HTTP_404_NOT_FOUND:
            message = f'Рецепт {recipe_basket.name} отсутвует в корзине'
            return Response(
                {'errors': message}, status=status.HTTP_400_BAD_REQUEST
            )
        items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = (AuthorOnly, )

    def get_queryset(self):
        return get_object_or_404(
            Recipe, id=self.kwargs.get('recipe.id')
        )

    def delete(self, request, recipe_id, format=None):
        recipe_favorite = get_object_or_404(
            Recipe, id=recipe_id
        )

        try:
            favorites = get_object_or_404(
                FavoriteRecipe, user=self.request.user,
                recipe=recipe_favorite
            )
        except status.HTTP_404_NOT_FOUND:
            message = f'Рецепт {recipe_favorite.name} отсутвует в избранном'
            return Response(
                {'errors': message}, status=status.HTTP_400_BAD_REQUEST
            )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
