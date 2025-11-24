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
from ..services.vagas_escolas import criar_vagas_em_lote, adicionar_vagas_ao_lote_por_processo
from ..serializers.vagas_escolas import VagasEscolasCreateSerializer
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
        # Filtro aplicado internamente (sem parâmetro de URL)
        qs = qs.filter(esta_checada=True)

        # Se houver qualquer valor informado nas colunas de utilizadas, somar utilizadas;
        # caso contrário, somar as colunas de vagas normais.
        ha_utilizadas = qs.filter(
            models.Q(vagas_precarias_utilizadas__isnull=False) |
            models.Q(vagas_definitivas_utilizadas__isnull=False)
        ).exists()
        if ha_utilizadas:
            totais = qs.aggregate(
                vagas_precarias=Sum('vagas_precarias_utilizadas'),
                vagas_definitivas=Sum('vagas_definitivas_utilizadas'),
            )
        else:
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
            'total_vagas_precarias': int(totais['vagas_precarias'] or 0),
            'total_vagas_definitivas': int(totais['vagas_definitivas'] or 0),
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

    @action(detail=False, methods=['post'], url_path='inclusao')
    def atualizar_vagas_lote(self, request, *args, **kwargs):
        """
        Recebe um payload equivalente ao do create (processo_uuid, processo_nome opcional, vagas=[...])
        e cria novas vagas em um lote já existente, identificado por processo_uuid.
        """
        response_data, status_code = adicionar_vagas_ao_lote_por_processo(request.data)
        return Response(response_data, status=status_code)
