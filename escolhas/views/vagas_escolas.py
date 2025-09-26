import logging
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import VagasEscolas
from ..serializers import VagasEscolasSerializer
from ..services import processar_criacao_vagas_lote
from ..utils import CustomPagination

logger = logging.getLogger(__name__)


class VagasEscolasViewSet(ModelViewSet):
    """
    ViewSet para gerenciar vagas das escolas.
    """
    queryset = VagasEscolas.objects.select_related('escola', 'escola__dre').all()
    serializer_class = VagasEscolasSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['escola__codigo_eol', 'escola__dre__codigo', 'concurso_uuid', 'concurso_nome']
    
    def create(self, request, *args, **kwargs):
        """
        Cria vagas das escolas em lote.
        
        Payload esperado:
        {
            "concurso_uuid": "123e4567-e89b-12d3-a456-426614174000", // opcional
            "concurso_nome": "Concurso Professor 2024", // opcional
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