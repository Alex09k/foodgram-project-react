from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, TagViewSet


router = routers.DefaultRouter()
router = DefaultRouter()


router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredient', IngredientViewSet, basename='ingredient')
router.register('tag', TagViewSet, basename='tag')


urlpatterns = [
    path('', include(router.urls)),

]    
