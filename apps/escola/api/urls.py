"""Rotas de URL do módulo escola."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from escola.api.views import DreViewSet, EscolaViewSet

router = DefaultRouter()
router.register(r"dres", DreViewSet, basename="dre")
router.register(r"escolas", EscolaViewSet, basename="escola")

urlpatterns = [
    path("", include(router.urls)),
]
