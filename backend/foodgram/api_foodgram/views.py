from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api_foodgram.filters import IngredientSearchFilter, RecipeFilter
from api_foodgram.models import Basket, FavoriteRecipe, Ingredient, Recipe, Tag
from api_foodgram.pagination import PagePagination
from api_foodgram.permissions import AuthorAdminOrReadOnly, SubscribeUser
from api_foodgram.serializers import (IngredientSerializer,
                                      RecipeCreateSerializer,
                                      RecipeHelpSerializer, RecipeSerializer,
                                      SubscribeSerializer, TagSerializer)
from api_foodgram.utils import get_basket
from users.models import Subscribe, User
from users.serializers import CustomUserSerializer


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        basket_recipe = Basket.objects.filter(user=user,
                                              recipe=recipe).exists()
        if request.method == 'POST':
            if basket_recipe:
                message = f'{recipe} уже добавлен в список покупок'
                return Response({'errors': message})
            Basket.objects.create(user=user, recipe=recipe)
            serializer = RecipeHelpSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not basket_recipe:
            message = f'{recipe} не найден'
            return Response({'errors': message},
                            status=status.HTTP_404_NOT_FOUND)
        Basket.objects.get(user=user,
                           recipe=recipe).delete()
        message = f'{recipe} удален из вашей корзины'
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        return get_basket(self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        fav_recipe = FavoriteRecipe.objects.filter(user=user,
                                                   recipe=recipe).exists()
        if request.method == 'POST':
            if fav_recipe:
                message = f'{recipe} уже добавлен в избранное'
                return Response({'errors': message})
            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = RecipeHelpSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not fav_recipe:
            message = f'{recipe} не найден'
            return Response({'errors': message},
                            status=status.HTTP_404_NOT_FOUND)
        FavoriteRecipe.objects.get(user=user,
                                   recipe=recipe).delete()
        message = f'{recipe} удален из избранного'
        return Response(message, status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class ListModelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


# class SubscriptionsViewSet(ListModelViewSet):
#     serializer_class = SubscribeSerializer
#     pagination_class = PagePagination
#     permission_classes = (SubscribeUser,)
#
#     def get_queryset(self):
#         subscriptions_queryset = self.request.user.subscriber.all()
#         subscriptions_list = subscriptions_queryset.values_list(
#             'author', flat=True
#         )
#         return User.objects.filter(id__in=subscriptions_list)
#
#
# class SubscribeViewSet(viewsets.ModelViewSet):
#     serializer_class = SubscribeSerializer
#     permission_classes = (SubscribeUser,)
#
#     def get_queryset(self):
#         return self.get_object_or_404(User, id=self.kwargs.get('user_id'))
#
#     def delete(self, request, user_id, format=None):
#         unsubs = get_object_or_404(User, id=user_id)
#         try:
#             subscribe = get_object_or_404(
#                 Subscribe,
#                 user=request.user,
#                 author=unsubs
#             )
#         except status.HTTP_404_NOT_FOUND:
#             message = f'Автор {unsubs} отсутствут в Ваших подписках.'
#             return Response(
#                 {'errors': message})
#         subscribe.delete()
#         return Response(status.HTTP_204_NO_CONTENT)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (UserMeOrUserProfile, )
    pagination_class = PagePagination
    serializer_class = CustomUserSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[SubscribeUser])
    def subscribe(self, request, *args, **kwargs):
        """Создание и удаление подписки."""
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response({'Подписка успешно создана': serializer.data},
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response('Успешная отписка',
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Объект не найден'},
                        status=status.HTTP_404_NOT_FOUND)

    @action(detail=False,
            methods=['get'],
            permission_classes=[SubscribeUser])
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        subscribes = Subscribe.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(pages, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
