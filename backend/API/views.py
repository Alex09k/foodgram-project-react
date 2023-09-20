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
from .permissions import IsAuthorAdminOrReadOnly
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from .paginators import RecipePagination
from .filters import IngredientFilter, RecipeFilter
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = RecipePagination
    filterset_class = RecipeFilter

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
    
    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, id):
        return self._create_or_destroy(
            request.method, request, id, Favourite, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        
    )
    def shopping_cart(self, request, id):
        return self._create_or_destroy(
            request.method, request, id, ShoppingCart, ShoppingCartSerializer
        )



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None



   





class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


           


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(followed__user=request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = FollowSerializer(pages, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('У Вас нет подписок.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        subscription = Follow.objects.filter(
            user=user.id, author=author.id
        )
        if user == author:
            return Response('На себя подписываться нельзя!',
                            status=status.HTTP_400_BAD_REQUEST)
        if subscription.exists():
            return Response(f'Вы уже подписаны на {author}',
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe = Follow.objects.create(
            user=user,
            author=author
        )
        subscribe.save()
        return Response(f'Вы подписались на {author}',
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        change_subscription = Follow.objects.filter(
            user=user.id, author=author.id
        )
        change_subscription.delete()
        return Response(f'Вы больше не подписаны на {author}',
                        status=status.HTTP_204_NO_CONTENT)


