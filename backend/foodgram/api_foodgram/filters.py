from django_filters import rest_framework as filters

from users.models import User

from .models import Ingredient, Tag


class RecipeFilterSet(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all())
    author = filters.ModelChoiceFilter(queryset=User.objects.all())


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
