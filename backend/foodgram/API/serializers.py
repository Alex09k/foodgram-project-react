from rest_framework import serializers

from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("name", "text", "Cooking_time","author","ingredients","tags")