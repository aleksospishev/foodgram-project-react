from api_foodgram.filters import IngredientSearchFilter, RecipeFilter
from api_foodgram.models import Basket, FavoriteRecipe, Ingredient, Recipe, Tag
from api_foodgram.pagination import PagePagination
from api_foodgram.permissions import AuthorAdminOrReadOnly, SubscribeUser
from api_foodgram.serializers import (IngredientSerializer,
                                      RecipeCreateSerializer,
                                      RecipeHelpSerializer, RecipeSerializer,
                                      SubscribeSerializer, TagSerializer)
from api_foodgram.utils import get_basket
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscribe, User


class ListModelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CreateDeleteModelViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     pagination_class = PagePagination
#     permission_classes = (permissions.AllowAny,)
#
#     def get_serializer_class(self):
#         if self.request.method in SAFE_METHODS:
#             return UserSerializer
#         return UserCreateSerializer
#
#     @action(detail=False,
#             methods=['GET'],
#             permission_classes=[permissions.IsAuthenticated])
#     def me(self, request):
#         serializer = UserSerializer(
#             request.user,
#             context={'request': request}
#         )
#         return Response(serializer.data)
#
#     @action(detail=False,
#             methods=['post'],
#             permission_classes=(permissions.IsAuthenticated,))
#     def set_password(self, request):
#         serializer = SetPasswordSerializer(request.user, data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except serializer.ValidationError as e:
#             return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
#         serializer.save()
#         return Response({'detail': 'Пароль успешно изменен'},
#                         status=status.HTTP_204_NO_CONTENT)
#
#     @action(detail=True,
#             methods=['post', 'delete'],
#             permission_classes=(permissions.IsAuthenticated,))
#     def subscribe(self, request, **kwargs):
#         author = get_object_or_404(User, id=kwargs['pk'])
#         user = request.user
#
#         if request.method == 'POST':
#             serializer = SubscribeSerializer(data={
#                 'user': user.id,
#                 'author': kwargs.get('pk')
#             }, context={"request": request})
#
#             try:
#                 serializer.is_valid(raise_exception=True)
#             except serializer.ValidationError as e:
#                 return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
#
#             # Если подписка существет / подписываемся на себя - рейзим 400
#             if Subscribe.objects.filter(
#                     user=user,
#                     author=author).exists() or author == user:
#                 return Response(
#                     {'errors': 'Подписка существует / подписка на себя'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             serializer.save(author=author, user=user)
#             return Response(serializer.data,
#                             status=status.HTTP_201_CREATED)
#
#         if not Subscribe.objects.filter(
#                 user=user,
#                 author=author).exists():
#             return Response(
#                 {'errors': 'Ошибка отписки (Вы не были подписаны)'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         Subscribe.objects.get(
#             user=user,
#             author=author).delete()
#         return Response(
#             'Вы успешно отписаны',
#             status=status.HTTP_204_NO_CONTENT
#         )
#
#     @action(detail=False,
#             methods=['get'],
#             permission_classes=[permissions.IsAuthenticated],
#             pagination_class=PagePagination)
#     def subscriptions(self, request):
#         user = request.user
#         subscribes = Subscribe.objects.filter(
#             user=user)
#         page = self.paginate_queryset(subscribes)
#         serializer = SubscribeSerializer(
#             page,
#             many=True,
#             context={'request': request}
#         )
#         return self.get_paginated_response(serializer.data)

class SubscriptionsViewSet(ListModelViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = PagePagination
    permission_classes = (SubscribeUser,)

    def get_queryset(self):
        subscriptions_queryset = self.request.user.subscriber.all()
        subscriptions_list = subscriptions_queryset.values_list(
            'author', flat=True
        )
        return User.objects.filter(id__in=subscriptions_list)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # def subscribe(self, request, **kwargs):
    #     author = get_object_or_404(User, id=kwargs['pk'])
    #     user = request.user
    #     if request.method == 'POST':
    #         serializer = SubscribeSerializer(data={
    #             'user': user.id,
    #             'author': kwargs.get('pk')
    #         }, context={"request": request})
    #
    #         try:
    #             serializer.is_valid(raise_exception=True)
    #         except serializer.ValidationError as e:
    #             return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    #
    #         if Subscribe.objects.filter(
    #                 user=user,
    #                 author=author).exists() or author == user:
    #             return Response(
    #                 {'errors': 'Подписка существует / подписка на себя'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         serializer.bulk_create(author=author, user=user)
    #         return Response(serializer.data,
    #                         status=status.HTTP_201_CREATED)
    #
    #     if not Subscribe.objects.filter(
    #             user=user,
    #             author=author).exists():
    #         return Response(
    #             {'errors': 'Ошибка отписки (Вы не были подписаны)'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     Subscribe.objects.get(
    #         user=user,
    #         author=author).delete()
    #     return Response(
    #         'Вы успешно отписаны',
    #         status=status.HTTP_204_NO_CONTENT
    #     )
    def get_queryset(self):
        return get_object_or_404(
            User, id=self.kwargs.get('user_id')
        )

    def create(self, request, *args, **kwargs):
        # author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = request.user
        serializer = SubscribeSerializer(
            data={
                'user': user.id,
                'author': kwargs.get('id')},
            context={"request": request})
        Subscribe.objects.create(author='author', user='user')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id, format=None):
        unsubs = get_object_or_404(User, id=user_id)
        try:
            subscribe = get_object_or_404(
                Subscribe,
                user=request.user,
                author=unsubs
            )
        except status.HTTP_404_NOT_FOUND:
            message = f'Автор {unsubs} отсутствут в Ваших подписках.'
            return Response(
                {'errors': message})
        subscribe.delete()
        return Response(status.HTTP_204_NO_CONTENT)
