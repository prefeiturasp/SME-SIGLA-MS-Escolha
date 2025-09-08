from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Escola
from ..serializers import (
    EscolaSerializer,
    EscolaSelectSerializer,
    EscolaListSerializer,
)
from ..utils import CustomPagination


class EscolaViewSet(viewsets.ModelViewSet):
    queryset = Escola.objects.select_related('dre').all()
    serializer_class = EscolaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome_oficial', 'codigo_eol', 'nome_dre', 'bairro']
    ordering_fields = ['criado_em', 'nome_oficial']
    ordering = ['-criado_em']
    pagination_class = CustomPagination
