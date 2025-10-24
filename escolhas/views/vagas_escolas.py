import logging
from django.db import models
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from ..models import VagasEscolas, VagasEscolasLote
from ..serializers import (
    VagasEscolasSerializer,
    VagasEscolasUtilizadasUpdateSerializer,
    VagaEscolaUtilizadaItemSerializer,
)
from ..services import processar_criacao_vagas_lote
from ..services.vagas_escolas import atualizar_vagas_utilizadas_por_processo
from ..utils import CustomPagination

logger = logging.getLogger(__name__)


class VagasEscolasViewSet(ModelViewSet):
    """
    ViewSet para gerenciar vagas das escolas.
    """
    queryset = VagasEscolas.objects.select_related('escola', 'escola__dre', 'lote').all()
    serializer_class = VagasEscolasSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['escola__codigo_eol', 'escola__dre__codigo', 'cargo_codigo']

    def get_queryset(self):
        qs = super().get_queryset()
        processo_uuid = self.request.query_params.get('processo_uuid')
        if processo_uuid:
            lote = VagasEscolasLote.objects.filter(processo_uuid=processo_uuid).order_by('-criado_em').first()
            if not lote:
                return VagasEscolas.objects.none()
            qs = qs.filter(lote=lote)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        totais = qs.aggregate(
            vagas_precarias=Sum('vagas_precarias'),
            vagas_definitivas=Sum('vagas_definitivas'),
        )
        dres = list(
            qs.values('escola__dre__codigo', 'escola__dre__nome', 'escola__dre__uuid')
              .distinct()
              .order_by('escola__dre__codigo')
        )
        dres_fmt = [
            {
                'codigo': d['escola__dre__codigo'],
                'nome': d['escola__dre__nome'],
                'uuid': d['escola__dre__uuid'],
            }
            for d in dres
        ]

        data = VagasEscolasSerializer(qs, many=True).data
        return Response({
            'vagas': data,
            'total_vagas': int(totais['vagas_precarias'] or 0) + int(totais['vagas_definitivas'] or 0),
            'dres': dres_fmt,
        })

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

    @action(detail=False, methods=['patch'], url_path='utilizadas')
    def utilizadas(self, request, *args, **kwargs):
        payload = VagaEscolaUtilizadaItemSerializer(data=request.data, many=True)
        payload.is_valid(raise_exception=True)
        vagas = payload.validated_data

        result = atualizar_vagas_utilizadas_por_processo(vagas)
        return Response(result)
