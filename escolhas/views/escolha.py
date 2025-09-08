from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Escolha
from ..serializers import (
    EscolhaSerializer,
    EscolhaSelectSerializer,
    EscolhaListSerializer,
)
from ..utils import CustomPagination


class EscolhaViewSet(viewsets.ModelViewSet):
    queryset = Escolha.objects.all()
    serializer_class = EscolhaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']
    pagination_class = CustomPagination
