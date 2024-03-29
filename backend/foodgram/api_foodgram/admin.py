from api_foodgram.models import (FavoriteRecipe, Ingredient, IngredientsRecipe,
                                 Recipe, Tag)
from django.contrib import admin
from users.models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user']
    list_filter = ['author']


class IngredientLine(admin.TabularInline):
    model = IngredientsRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientLine, ]
    list_display = ['name',
                    'author',
                    'pub_date',
                    'count_in_favorite',
                    ]
    search_fields = ['name', 'author']
    list_filter = ['name', 'author', 'tags', 'pub_date']
    readonly_fields = ('count_in_favorite',)

    def count_in_favorite(self, obj):
        return obj.Favorite_recipe.all().count()

    count_in_favorite.short_description = 'кол-во раз добавления в избранное'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name', ]
    list_filter = ['name', ]


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ['name', 'slug']
    list_filter = ['name', 'slug']


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user']
    search_fields = ['recipe']
    list_filter = ['recipe', 'user']


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
