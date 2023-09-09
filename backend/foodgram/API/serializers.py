from rest_framework import serializers

from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart, IngredientIntermediate,
                            Tag)
from django.db import transaction
from rest_framework.fields import IntegerField, SerializerMethodField

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id","name", "units")



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(
        source='ingredient.units'
    )

    class Meta:
        model = IngredientIntermediate
        fields = ('id', 'name', 'units', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    
    ingredients = IngredientRecipeSerializer(source='ingredient_contained',
                                             many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
   
    

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                   'name', 'text',
                  'Cooking_time')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientIntermediate
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'name',
                  'text', 'cooking_time',)

    def validate(self, data):
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Тег обязателен для заполнения!'
            })
        tags_set = set()
        for tag in tags:
            if tag in tags_set:
                raise serializers.ValidationError({
                    'tags': f'Тег {tag} уже существует, внесите новый!'
                })
            tags_set.add(tag)
        ingredients = data['ingredients']
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Необходимо внести ингредиенты!'
            })
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент {ingredient} уже существует,'
                                   ' внесите новый!'
                })
            ingredients_set.add(ingredient_id)
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
        cooking_time = data['cooking_time']
        if int(cooking_time) < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0!'
            })
        return data

    def add_ingredients(self, ingredients, recipe):
        new_ingredients = [IngredientIntermediate(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientIntermediate.objects.bulk_create(new_ingredients)

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    @transaction.atomic
    def create(self, validated_data):
        
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe



#     def to_representation(self, instance):
#         return representation(self.context, instance, RecipeSerializer)



