"""
URL configuration for the concursos module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CargoViewSet, ConcursoViewSet, EscolhaViewSet

router = DefaultRouter()
router.register(r'cargos', CargoViewSet, basename='cargo') #TODO REMOVE AFTER TESTS
router.register(r'concursos', ConcursoViewSet, basename='concurso')#TODO REMOVE AFTER TESTS
router.register(r'escolhas', EscolhaViewSet, basename='escolha')

urlpatterns = [
    path('', include(router.urls)),
] 