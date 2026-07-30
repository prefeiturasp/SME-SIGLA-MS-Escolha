"""URL configuration for the escolhas module."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EscolhaViewSet, ExtracaoDadosViewSet

router = DefaultRouter()
router.register(r"escolhas", EscolhaViewSet, basename="escolha")
router.register(
    r"extracao-dados", ExtracaoDadosViewSet, basename="extracao-dados"
)

urlpatterns = [
    path("", include(router.urls)),
]
