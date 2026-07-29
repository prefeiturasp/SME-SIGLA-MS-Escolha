"""URL configuration for the escolhas module."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DreViewSet,
    EscolaViewSet,
    EscolhaViewSet,
    ExtracaoDadosViewSet,
    ParametrizacaoViewSet,
    VagasEscolasViewSet,
)

router = DefaultRouter()
router.register(r"escolhas", EscolhaViewSet, basename="escolha")
router.register(r"escolas", EscolaViewSet, basename="escola")
router.register(r"dres", DreViewSet, basename="dre")
router.register(
    r"extracao-dados", ExtracaoDadosViewSet, basename="extracao-dados"
)
router.register(
    r"vagas-escolas", VagasEscolasViewSet, basename="vagas-escolas"
)
router.register(
    r"parametrizacao", ParametrizacaoViewSet, basename="parametrizacao"
)

urlpatterns = [
    path("", include(router.urls)),
]
