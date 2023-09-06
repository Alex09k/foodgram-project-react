# from django.shortcuts import render
# from rest_framework import  viewsets
# # Create your views here.
# class RecipeViewSet(viewsets.ModelViewSet):
#     pass
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from recipes.models import (Favourite, Follow, Ingredient, Recipe, ShoppingCart,
                            Tag)
from .serializers import RecipeSerializer

# View-функция cat_list() будет обрабатывать только запросы GET и POST, 
# запросы других типов будут отклонены,
# так что в теле функции их можно не обрабатывать


class Receps(APIView):
    def get(self, request):
        recipe = Recipe.objects.all()

        serializers = RecipeSerializer(recipe, many=True)
        return Response(serializers.data)
    
    def post(self, request):
        serializer = RecipeSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# @api_view(['GET', 'POST'])
# def RecipeViewSet(request):
#     if request.method == 'POST':
#         serializer = RecipeSerializer(data=request.data, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     cats = Recipe.objects.all()
#     serializer = RecipeSerializer(cats, many=True)
#     return Response(serializer.data) 

# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def Recipe_detal(request, pk):
#     recepe = Recipe.objects.get(pk=pk)
#     if request.method == 'PUT' or request.method == 'PATCH':
#         serializer = RecipeSerializer(recepe, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         recepe.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     serializer = RecipeSerializer(recepe)
#     return Response(serializer.data)



