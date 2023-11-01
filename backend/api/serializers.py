
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer

from .utils import representation
from users.models import CustomUser
from foodgram.constants import (INGREDIENT_MAX_AMOUNT,
                                INGREDIENT_MIN_AMOUNT,
                                COOKING_TIME_MIN_VALUE,
                                COOKING_TIME_MAX_VALUE)
from recipes.models import (Favorite,
                            Follow,
                            Ingredient,
                            Recipe,
                            ShoppingCart,
                            IngredientRecipe,
                            Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
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


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit')


class RecipeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели IngredientRecipe"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(
        max_value=INGREDIENT_MAX_AMOUNT,
        min_value=INGREDIENT_MIN_AMOUNT
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


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

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=recipe).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        max_value=COOKING_TIME_MAX_VALUE,
        min_value=COOKING_TIME_MIN_VALUE
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'name',
                  'text', 'cooking_time', 'image')

    def validate_ingredients(self, value):
        """Валидация поля ингредиентов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один ингредиент'
            )
        ingredients_id_set = set()
        for item in value:
            ingredient_id = item['ingredient']['id']
            if ingredient_id in ingredients_id_set:
                raise serializers.ValidationError(
                    'Указано несколько одинаковых ингредиентов'
                )
            ingredients_id_set.add(ingredient_id)
        return value

    def validate_tags(self, value):
        """Валидаци поля тегов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один тег'
            )
        return value

    def add_ingredients(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient in ingredients:
            ingredient_amount = ingredient.pop('amount')
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            recipe_ingredient = IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient_amount
            )
            recipe_ingredients.append(recipe_ingredient)
        IngredientRecipe.objects.abulk_create(recipe_ingredient)

    @transaction.atomic
    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        recipe.tags.clear()
        recipe.ingredients.clear()
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
        if user.favorites.filter(recipe=recipe).exists():
            raise serializers.ValidationError('Рецепты не могут повторяться!')
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
        request = self.context['request']
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
        fields = ('user', 'author')

    def create(self, validated_data):
        author = validated_data['author']
        author = get_object_or_404(CustomUser, pk=author.get('id'))
        user = CustomUser.objects.get(id=validated_data['user']['id'])
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
