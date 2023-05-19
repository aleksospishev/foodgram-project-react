from django.http import HttpResponse

from .models import IngredientsRecipe


def get_basket(user):
    user_basket = user.basket.all()
    recipe_id = user_basket.values_list('recipe', flat=True)
    ingredient_amount = IngredientsRecipe.objects.filter(
        recipe__in=recipe_id).select_related('ingredient')
    uniq = []
    ingredients = {}
    for item in ingredient_amount:
        name = (
            item.ingredient.name + ' ('
            + item.ingredient.measurement_unit + ') - '
        ).capitalize()
        if item.ingredient.id in uniq:
            ingredients[name] += item.amount
        else:
            ingredients[name] = item.amount
            uniq.append(item.ingredient.id)
    basket_text = (
        'Список покупок.' + 'Выбрано рецептов:' + str(user_basket.count())
    )
    for ingredient, amount in ingredients.items():
        basket_text = (
            basket_text + ingredient + str(amount)
        )
    return HttpResponse(basket_text, content_type='text/plain')
