from django.contrib import admin

from .models import (Ingredient, Tag, Recipe)


class IngredientAdmin(admin.ModelAdmin):
    """в понели администратора модель Ингридиен."""
    list_display = ('id', 'name', 'units')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    """в понели администратора модель Тега."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    """Представляет модель Recipe в интерфейсе администратора."""
    list_display = ('id', 'name', 'author')
    search_fields = ('author', 'name', 'tags')
    empty_value_display = '-пусто-' 



admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
