"""Módulo views/dre."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from ..models import Dre
from ..serializers import DreSerializer
from ..utils import CustomPagination


class DreViewSet(viewsets.ModelViewSet):
    """Define DreViewSet."""
    queryset = Dre.objects.all()
    serializer_class = DreSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["nome", "sigla", "codigo"]
    ordering_fields = ["criado_em", "nome"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination
