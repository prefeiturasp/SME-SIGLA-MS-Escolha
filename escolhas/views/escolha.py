from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action

from ..choices import SituacaoChoices
from ..models import Escolha
from ..serializers import (
    EscolhaSerializer,
    EscolhaSelectSerializer,
    EscolhaListSerializer,
    EscolhaReconvocacaoSerializer,
)
from ..utils import CustomPagination


class EscolhaViewSet(viewsets.ModelViewSet):
    queryset = Escolha.objects.all()
    serializer_class = EscolhaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'candidato_uuid': ['exact'],
        'situacao': ['exact', 'in'],
    }
    search_fields = ['situacao', 'tipo_vaga']
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'busca']:
            return EscolhaListSerializer
        if self.action == 'select':
            return EscolhaSelectSerializer
        if self.action == 'reconvocacao':
            return EscolhaReconvocacaoSerializer
        return super().get_serializer_class()

    @action(methods=['post'], detail=False, url_path='busca')
    def busca(self, request):
        candidato_ids = request.data.get('candidato_uuid', [])
        if not isinstance(candidato_ids, list):
            return Response(
                {'detail': 'candidato_uuid deve ser uma lista de UUIDs.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(candidato_uuid__in=candidato_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='reconvocacao')
    def reconvocacao(self, request):
        """
        Endpoint para buscar escolhas com situação de reconvocação.
        Retorna apenas uuid e candidato_uuid.
        """
        queryset = self.get_queryset().filter(situacao=SituacaoChoices.RECONVOCACAO)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
