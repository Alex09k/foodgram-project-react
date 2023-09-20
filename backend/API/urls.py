# from django.urls import include, path

# from rest_framework import routers
# from rest_framework.routers import DefaultRouter
# from .views import RecipeViewSet, IngredientViewSet, TagViewSet, CustomUserViewSet

# app_name = 'api'
# router = routers.DefaultRouter()
# router = DefaultRouter()


# router.register('recipes', RecipeViewSet, basename='recipes')
# router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register('tags', TagViewSet, basename='tag')
# router.register('users', CustomUserViewSet, basename='users')


# urlpatterns = [
#     path('', include(router.urls)),
    
#     path('auth/', include('djoser.urls.authtoken')),
    

# ]    




from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]