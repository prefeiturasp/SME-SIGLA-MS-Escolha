"""
URL configuration for the concursos module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CargoViewSet, ConcursoViewSet

router = DefaultRouter()
router.register(r'cargos', CargoViewSet, basename='cargo')
router.register(r'concursos', ConcursoViewSet, basename='concurso')

urlpatterns = [
    path('', include(router.urls)),
] 