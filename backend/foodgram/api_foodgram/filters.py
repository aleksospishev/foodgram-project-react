from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter
from users.models import User

from .models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_method')
    is_favorited = filters.NumberFilter(
        method='is_favorited_method')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_method(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(Favorite_recipe__user=self.request.user)
        return queryset

    def is_in_shopping_cart_method(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(basket__user=self.request.user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    # name = filters.CharFilter(
    #     lookup_expr='istartswith'
    # )
    #
    # class Meta:
    #     model = Ingredient
    #     fields = ('name',)
    search_param = 'name'