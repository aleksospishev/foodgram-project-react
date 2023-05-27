from django.db.models import Sum
from django.http import HttpResponse

from .models import IngredientsRecipe


def get_basket(user):
    user_basket = user.basket.all()
    # recipe_id = user_basket.values_list('recipe', flat=True)
    ingredient_amount = IngredientsRecipe.objects.filter(
        recipe__user=user_basket).values(
        'ingredient__name',
        'ingredient__measurement_unit').annotate(
        amounts=Sum('ingredient__name')
    ).order_by('amounts')
    basket_text = (
        'Список покупок.' + '\n'
        + 'Выбрано рецептов:' + str(user_basket.count()) + '\n')
    for ingredient in ingredient_amount:
        basket_text += (
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    return HttpResponse(basket_text, content_type='text/plain')
