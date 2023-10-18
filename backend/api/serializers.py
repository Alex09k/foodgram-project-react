from rest_framework import serializers
from django.shortcuts import get_object_or_404

from recipes.models import (Favorite, Follow,
                            Ingredient, Recipe, ShoppingCart,
                            IngredientRecipe, Tag)
from django.db import transaction

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from foodgram.constants import COOKING_TIME_MIN_VALUE, INGREDIENT_MIN_AMOUNT

from .utils import representation

from users.models import CustomUser

from rest_framework import status

TAGS_UNIQUE_ERROR = 'Теги не могут повторяться!'
TAGS_EMPTY_ERROR = 'Рецепт не может быть без тегов!'
INGREDIENTS_UNIQUE_ERROR = 'Ингредиенты не могут повторяться!'
INGREDIENTS_EMPTY_ERROR = 'Без ингредиентов рецепта не бывает!'
INGREDIENT_MIN_AMOUNT_ERROR = (
    'Количество ингредиента не может быть меньше 1!'
)
INGREDIENT_DOES_NOT_EXIST = 'Такого ингредиента не существует!'
COOKING_TIME_MIN_ERROR = (
    'Время приготовления не может быть меньше одной минуты!'
)
RECIPE_UNIQUE_ERROR = 'Рецепты не могут повторяться!'



class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')



class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.follower.filter(user_id=user.id).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    @transaction.atomic
    def create(self, validated_data):
        user = super(CustomUserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(source='ingredient_recipe',
                                             many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'text', 'cooking_time', 'image',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return self._obj_exists(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._obj_exists(obj, ShoppingCart)

    def _obj_exists(self, recipe, name_class):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return name_class.objects.filter(user=request.user,
                                         recipe=recipe).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'name',
                  'text', 'cooking_time', 'image')

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
        # if data['cooking_time'] < COOKING_TIME_MIN_VALUE:
        #     raise serializers.ValidationError(COOKING_TIME_MIN_ERROR)
        # if len(data['tags']) == 0:
        #     raise serializers.ValidationError(TAGS_EMPTY_ERROR)
        # if len(data['tags']) > len(set(data['tags'])):
        #     raise serializers.ValidationError(TAGS_UNIQUE_ERROR)
        # if len(data['ingredients']) == 0:
        #     raise serializers.ValidationError(INGREDIENTS_EMPTY_ERROR)
        # id_ingredients = []
        # for ingredient in data['ingredients']:
        #     if ingredient['amount'] < INGREDIENT_MIN_AMOUNT:
        #         raise serializers.ValidationError(
        #             INGREDIENT_MIN_AMOUNT_ERROR.format(
        #                 min_value=INGREDIENT_MIN_AMOUNT,
        #             )
        #         )
        #     id_ingredients.append(ingredient['id'])
        # if len(id_ingredients) > len(set(id_ingredients)):
        #     raise serializers.ValidationError(INGREDIENTS_UNIQUE_ERROR)
        # return data
 
        
   
    def add_ingredients(self, ingredients, recipe):
        new_ingredients = [IngredientRecipe(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients]
        IngredientRecipe.objects.bulk_create(new_ingredients)
       
    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        # self.add_tags(tags, recipe)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
        # self.add_tags(validated_data.pop('tags'), recipe)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            recipe.tags.set(tags)
        self.add_ingredients(validated_data.pop('ingredients'), recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return representation(self.context, instance, RecipeSerializer)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(RECIPE_UNIQUE_ERROR)
        return data

    def to_representation(self, instance):
        return representation(
            self.context,
            instance.recipe,
            RecipeListSerializer)


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
        
    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeListSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
    

class CreateFollowSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def validate(self, data):
        user = data['user']['id']
        author = data['author']['id']
        follow_exist = Follow.objects.filter(
            user__id=user, author__id=author
        ).exists()
        if user == author:
            raise serializers.ValidationError(
                {"errors": 'Вы не можете подписаться на самого себя'}
            )
        elif follow_exist:
            raise serializers.ValidationError({"errors": 'Вы уже подписаны'})
        return data

    def create(self, validated_data):
        author = validated_data.get('author')
        author = get_object_or_404(CustomUser, pk=author.get('id'))
        user = CustomUser.objects.get(id=validated_data["user"]["id"])
        Follow.objects.create(user=user, author=author)
        return validated_data        


class ShoppingCartSerializer(RecipeListSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return representation(
            self.context,
            instance.recipe,
            RecipeListSerializer)
