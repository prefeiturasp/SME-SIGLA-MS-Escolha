"""
URL configuration for the concursos module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EscolhaViewSet, EscolaViewSet, DreViewSet, VagasEscolasViewSet, ParametrizacaoViewSet

router = DefaultRouter()
router.register(r'escolhas', EscolhaViewSet, basename='escolha')
router.register(r'escolas', EscolaViewSet, basename='escola')
router.register(r'dres', DreViewSet, basename='dre')
router.register(r'vagas-escolas', VagasEscolasViewSet, basename='vagas-escolas')
router.register(r'parametrizacao', ParametrizacaoViewSet, basename='parametrizacao')

urlpatterns = [
    path('', include(router.urls)),
] 