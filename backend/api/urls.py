from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import (RecipeViewSet,
                    IngredientViewSet,
                    TagViewSet,
                    CustomUserViewSet)


app_name = 'api'
router = routers.DefaultRouter()
router = DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
