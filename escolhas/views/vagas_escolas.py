import logging
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import VagasEscolas, VagasEscolasLote
from ..serializers import VagasEscolasSerializer
from ..services import processar_criacao_vagas_lote
from ..utils import CustomPagination

logger = logging.getLogger(__name__)


class VagasEscolasViewSet(ModelViewSet):
    """
    ViewSet para gerenciar vagas das escolas.
    """
    queryset = VagasEscolas.objects.select_related('escola', 'escola__dre', 'lote').all()
    serializer_class = VagasEscolasSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['escola__codigo_eol', 'escola__dre__codigo', 'concurso_uuid', 'concurso_nome']
    
    def list(self, request, *args, **kwargs):
        processo_uuid = request.query_params.get('processo_uuid')
        if processo_uuid:
            lote = VagasEscolasLote.objects.filter(processo_uuid=processo_uuid).order_by('-criado_em').first()
            if lote is None:
                return Response({'results': [], 'count': 0}, status=status.HTTP_200_OK)
            qs = self.queryset.filter(lote=lote)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Cria vagas das escolas em lote.

        Payload esperado:
        {
            "processo_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "processo_nome": "Concurso de Professor de Matemática",
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "123456",
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo"
                }
            ]
        }
        """
        response_data, status_code = processar_criacao_vagas_lote(request.data)
        return Response(response_data, status=status_code)