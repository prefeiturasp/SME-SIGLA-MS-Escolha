"""Módulo views/dre."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from core.utils import CustomPagination
from escola.models import Dre
from escola.serializers import DreSerializer


class DreViewSet(viewsets.ModelViewSet):
    """Expõe CRUD de DREs com busca, ordenação e paginação."""

    queryset = Dre.objects.all()
    serializer_class = DreSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["nome", "sigla", "codigo"]
    ordering_fields = ["criado_em", "nome"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination
