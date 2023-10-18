from django.contrib import admin

from .models import (Ingredient, Tag, Recipe, IngredientRecipe,
                     Favorite, Follow,
                     ShoppingCart)


class IngredientRecipeInline(admin.TabularInline):
    """в понели администратора модель IngredientIntermediate."""
    model = IngredientRecipe
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    """в понели администратора модель Ингридиены."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    """в понели администратора модель Тега."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    """в понели администратора модель Recipe."""
    list_display = ('id', 'name', 'author')
    search_fields = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'

    @staticmethod
    def amount_ingredients(obj):
        return "\n".join([i[0] for i in obj.ingredients.values_list('name')])

    def is_favourited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    @staticmethod
    def amount_favourite(obj):
        return obj.favourites.count()

    @staticmethod
    def amount_tags(obj):
        return "\n".join([i[0] for i in obj.tags.values_list('name')])


class FavoriteAdmin(admin.ModelAdmin):
    """в понели администратора модель Favourite."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """в понели администратора модель Follow."""
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """в понели администратора модель ShoppingCart."""
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
