"""
URL configuration for the concursos module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  EscolhaViewSet

router = DefaultRouter()
router.register(r'escolhas', EscolhaViewSet, basename='escolha')

urlpatterns = [
    path('', include(router.urls)),
] 