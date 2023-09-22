
from rest_framework import  viewsets, status
from recipes.models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart, IngredientRecipe,
                            Tag)
from users.models import CustomUser

from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, CustomUserSerializer, RecipeCreateSerializer, FollowSerializer, FavoriteSerializer, ShoppingCartSerializer
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

from django.http import FileResponse


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        
        if self.action == 'list':
            
            return RecipeSerializer
        
        return RecipeCreateSerializer 
    
    @staticmethod
    def create_recipe(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def delete_recipe(model, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = get_object_or_404(model, user=user, recipe=recipe)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _create_or_destroy(self, http_method, recipe, key,
                           model, serializer):
        if http_method == 'POST':
            return self.create_recipe(request=recipe, pk=key,
                                      serializers=serializer)
        return self.delete_recipe(request=recipe, pk=key, model=model)
    
    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self._create_or_destroy(
            request.method, request, pk, Favorite, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        
    )
    def shopping_cart(self, request, pk):
        return self._create_or_destroy(
            request.method, request, pk, ShoppingCart, ShoppingCartSerializer
        )
    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = IngredientRecipe.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount

            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')

        return FileResponse(open(file, 'rb'), as_attachment=True)

    
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
    search_fields = ('^name', )


           


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


