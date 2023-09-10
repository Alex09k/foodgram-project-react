from django.shortcuts import render
from rest_framework import  viewsets
from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import CustomUser

from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, CustomUserSerializer, RecipeWriteSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        
        if self.action == 'list':
            
            return RecipeSerializer
        
        return RecipeWriteSerializer 


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer



class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = RecipeSerializer    



class FollowViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = RecipeSerializer            


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


