from django.conf import settings
from django.core.validators import MinValueValidator, validate_slug
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Базовая модель Ингредиента,
    опиcывается полями name, unit, text

    name - название ингредиента
    unit - единица измерения мл, л, гр, кг, шт
    text - некоторые ингредиенты имеют специфическое происхождение,
    например продается в определенных магазинах или же его можно заменить
    на что тоиное, например коровье молоко заменить овсяным немолоком
    """
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=settings.LENG_CHARFIELD,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.LENG_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    """
    Базовая модель Тэг
    опиcывается полями name, color, slug
    name - название тэга
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.LENG_CHARFIELD,
        unique=True,
        help_text=f'название tag, max = {settings.LENG_CHARFIELD} sym'
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=settings.LENG_HEX,
        help_text='цвет в формате HEX',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=settings.LENG_CHARFIELD,
        unique=True,
        validators=[validate_slug],
        help_text=f'слаг tag, max = {settings.LENG_CHARFIELD} sym'
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}, {self.slug}'


class Recipe(models.Model):
    """
    Базовая модель Ингредиента,
    опиcывается полеями author, pub_date, name, text, image, ingredients,
    cooking_time, tags

    author - пользователь, который публикует рецепт
    pub_date - дата публикации рецепта,
    name - название блюда,
    text - описание
    оценка сложности приготовления по мнению автора
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    name = models.CharField(
        verbose_name='Название блюда',
        help_text='Введите название блюда',
        max_length=settings.LENG_CHARFIELD,
        db_index=True
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text="Опишите историю блюда, ваши впечатления или что то иное"
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Выберите фото блюда',
        upload_to='api_foodgram/media/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты для вашего блюда',
        through='IngredientsRecipe',

    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1),),
        help_text='Время приготовления в мин.'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Название тега',
        help_text='Выберите тег')

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]

    def __str__(self):
        return (f'{self.name} для {self.tags} временем приготовления '
                f'{self.cooking_time}'
                f'добавлен')


class IngredientsRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты'
    )
    amount = models.FloatField(
        verbose_name='Количество ингредиентов',
        validators=[MinValueValidator(0.01)]
    )

    class Meta:

        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]

    def __str__(self):
        return f'{self.ingredient}{self.amount}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='Favorite_recipe',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='Favorite_recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} понравился {self.recipe}'


class Basket(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='basket'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='basket'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_basket',
            )
        ]

    def __str__(self):
        return f'{self.recipe}'
