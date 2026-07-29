"""Rotas de URL do módulo vagas_escolas."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from vagas_escolas.api.views import VagasEscolasViewSet

router = DefaultRouter()
router.register(
    r"vagas-escolas", VagasEscolasViewSet, basename="vagas-escolas"
)

urlpatterns = [
    path("", include(router.urls)),
]
