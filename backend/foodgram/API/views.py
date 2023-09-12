from django.shortcuts import render
from rest_framework import  viewsets, status
from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import CustomUser

from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, CustomUserSerializer, RecipeWriteSerializer, FollowSerializer, FavoriteSerializer, ShoppingCartSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    

    def get_serializer_class(self):
        
        if self.action == 'list':
            
            return RecipeSerializer
        
        return RecipeWriteSerializer 
    
    @staticmethod
    def create_recipe(request, id, serializers):
        data = {'user': request.user.id, 'recipe': id}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def delete_recipe(self, model, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        user = self.request.user
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _create_or_destroy(self, http_method, recipe, key,
                           model, serializer):
        if http_method == 'POST':
            return self.create_object(request=recipe, id=key,
                                      serializers=serializer)
        return self.delete_object(request=recipe, id=key, model=model)
    
    
    def favorite(self, request, id):
        return self._create_or_destroy(
            request.method, request, id, Favourite, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        
    )
    def shopping_cart(self, request, id):
        return self._create_or_destroy(
            request.method, request, id, ShoppingCart, ShoppingCartSerializer
        )



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer



   





class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


           


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions')
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    
    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe')
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if user == author:
            return Response(
                {'errors': 'На себя нельзя подписаться / отписаться'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Follow.objects.filter(
            author=author, user=user)
        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'errors': 'Нельзя подписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            queryset = Follow.objects.create(author=author, user=user)
            serializer = FollowSerializer(
                queryset, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'errors': 'Нельзя отписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



