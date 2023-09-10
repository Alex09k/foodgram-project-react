from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, TagViewSet, CustomUserViewSet


router = routers.DefaultRouter()
router = DefaultRouter()


router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredient', IngredientViewSet, basename='ingredient')
router.register('tag', TagViewSet, basename='tag')
router.register('user', CustomUserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),

]    
