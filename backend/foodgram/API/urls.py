from django.urls import include, path

from rest_framework import routers
from rest_framework.routers import DefaultRouter


router = routers.DefaultRouter()
router_v1 = DefaultRouter()


router_v1.register('recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router_v1.urls)),

]    
