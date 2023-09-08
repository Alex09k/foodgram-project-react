from rest_framework import serializers

from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("name", "units")


class TaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("name", "color", "slug", "recipes")


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(read_only=True, many=True)
    tags = TaSerializer(read_only=True, many=True)
    
    class Meta:
        model = Recipe
        fields = ("id", "name", "image",  "text", "Cooking_time","author","ingredients","tags")





       