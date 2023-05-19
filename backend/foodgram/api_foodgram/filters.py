from django_filters.rest_framework import filters, FilterSet

from users.models import User

from .models import Ingredient, Tag, Recipe


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        # label='tags',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_basket'
    )
    is_favorited = filters.NumberFilter(
        method='filter_favorite'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def is_favorite(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__author=self.request.user)
        return queryset

    def in_basket(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_basket__author=self.request.user)
        return queryset


class IngredientSearchFilter(FilterSet):
    name = filters.CharFilter(
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
