from django.contrib import admin

from .models import (Ingredient, Tag, Recipe, IngredientIntermediate)


class IngredientRecipeInline(admin.TabularInline):
    """в понели администратора модель IngredientIntermediate."""
    model = IngredientIntermediate




class IngredientAdmin(admin.ModelAdmin):
    """в понели администратора модель Ингридиен."""
    list_display = ('id', 'name', 'units')
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

    



admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)

