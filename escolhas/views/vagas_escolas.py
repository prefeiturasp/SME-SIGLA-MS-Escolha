"""Módulo views/vagas_escolas."""
from __future__ import annotations
from typing import Any
import logging
from django.db import models
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from escolhas.middleware import get_correlation_id
from ..models import VagasEscolas, VagasEscolasLote
from ..serializers import VagaEscolaUtilizadaItemSerializer, VagasEscolasSerializer
from ..services import processar_criacao_vagas_lote
from ..services.exceptions import TipoUEDesabilitadoException
from ..services.vagas_escolas import adicionar_vagas_ao_lote_por_processo, atualizar_vagas_utilizadas_por_processo
logger = logging.getLogger(__name__)

class VagasEscolasViewSet(ModelViewSet):
    """ViewSet para gerenciar vagas das escolas."""
    queryset = VagasEscolas.objects.select_related('escola', 'escola__dre', 'lote').all()
    serializer_class = VagasEscolasSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['escola__codigo_eol', 'escola__dre__codigo', 'cargo_codigo']

    def get_queryset(self) -> Any:
        """Executa get queryset."""
        qs = super().get_queryset()
        processo_uuid = self.request.query_params.get('processo_uuid')
        if processo_uuid:
            lote = VagasEscolasLote.objects.filter(processo_uuid=processo_uuid).order_by('-criado_em').first()
            if not lote:
                return VagasEscolas.objects.none()
            qs = qs.filter(lote=lote)
        return qs

    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Executa list."""
        logger.info('Listando vagas das escolas', extra={'correlation_id': get_correlation_id(), 'method': request.method, 'path': request.path, 'params': request.query_params, 'user': request.user})
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.filter(esta_checada=True)
        ha_utilizadas = qs.filter(models.Q(vagas_precarias_utilizadas__isnull=False) | models.Q(vagas_definitivas_utilizadas__isnull=False)).exists()
        if ha_utilizadas:
            totais = qs.aggregate(vagas_precarias=Sum('vagas_precarias_utilizadas'), vagas_definitivas=Sum('vagas_definitivas_utilizadas'))
        else:
            totais = qs.aggregate(vagas_precarias=Sum('vagas_precarias'), vagas_definitivas=Sum('vagas_definitivas'))
        dres = list(qs.values('escola__dre__codigo', 'escola__dre__nome', 'escola__dre__uuid').distinct().order_by('escola__dre__codigo'))
        dres_fmt = [{'codigo': d['escola__dre__codigo'], 'nome': d['escola__dre__nome'], 'uuid': d['escola__dre__uuid']} for d in dres]
        data = VagasEscolasSerializer(qs, many=True).data
        return Response({'vagas': data, 'total_vagas': int(totais['vagas_precarias'] or 0) + int(totais['vagas_definitivas'] or 0), 'total_vagas_precarias': int(totais['vagas_precarias'] or 0), 'total_vagas_definitivas': int(totais['vagas_definitivas'] or 0), 'dres': dres_fmt})

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Cria vagas das escolas em lote.

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
        logger.info('Criando vagas das escolas em lote', extra={'correlation_id': get_correlation_id(), 'method': request.method, 'path': request.path, 'params': request.query_params, 'processo_uuid': request.data.get('processo_uuid'), 'processo_nome': request.data.get('processo_nome'), 'vagas': len(request.data.get('vagas', [])), 'user': request.user})
        try:
            response_data, status_code = processar_criacao_vagas_lote(request.data)
            return Response(response_data, status=status_code)
        except TipoUEDesabilitadoException as exc:
            msg = str(exc)
            logger.error(f'Tipo UE desabilitado: {msg}')
            return Response({'detail': msg, 'code': 'TIPO_UE_DESABILITADO'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            msg = str(exc)
            logger.error(f'Erro ao criar vagas em lote: {msg}')
            return Response({'detail': msg, 'code': 'ERRO_AO_CRIAR_VAGAS_EM_LOTE'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['patch'], url_path='utilizadas')
    def utilizadas(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Executa utilizadas."""
        logger.info('Atualizando vagas utilizadas', extra={'correlation_id': get_correlation_id(), 'method': request.method, 'path': request.path, 'params': request.query_params, 'data': request.data, 'user': request.user})
        payload = VagaEscolaUtilizadaItemSerializer(data=request.data, many=True)
        payload.is_valid(raise_exception=True)
        vagas = payload.validated_data
        result = atualizar_vagas_utilizadas_por_processo(vagas)
        return Response(result)

    @action(detail=False, methods=['post'], url_path='inclusao')
    def atualizar_vagas_lote(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Recebe um payload equivalente ao do create (processo_uuid,.

        processo_nome opcional, vagas=[...])
        e cria novas vagas em um lote já existente, identificado por
        processo_uuid.
        """
        response_data, status_code = adicionar_vagas_ao_lote_por_processo(request.data)
        return Response(response_data, status=status_code)

    @action(detail=False, methods=['get'], url_path='por-cargo-e-escolas')
    def por_cargo_e_escolas(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Executa por cargo e escolas."""
        logger.info('Buscando vagas por cargo e escolas', extra={'correlation_id': get_correlation_id(), 'method': request.method, 'path': request.path, 'user': request.user, 'params': request.query_params})
        codigo_cargo = request.query_params.get('cargo_codigo')
        eols = request.query_params.getlist('codigo_eol') or (request.query_params.get('codigo_eol__in', '').split(',') if request.query_params.get('codigo_eol__in') else [])
        qs = VagasEscolas.objects.select_related('escola')
        if codigo_cargo:
            qs = qs.filter(cargo_codigo=codigo_cargo)
        if eols:
            qs = qs.filter(escola__codigo_eol__in=eols)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='por-processo')
    def excluir_por_processo(self, request: Any) -> Any:
        """Remove lotes de vagas (e vagas em cascata) do processo informado.

        Query: processo_uuid=<uuid>.
        """
        processo_uuid = request.query_params.get('processo_uuid')
        if not processo_uuid:
            return Response({'detail': 'processo_uuid é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = VagasEscolasLote.objects.filter(processo_uuid=processo_uuid).delete()
        logger.info('Lotes de vagas excluídos por processo', extra={'correlation_id': get_correlation_id(), 'processo_uuid': processo_uuid, 'lotes_excluidos': deleted})
        return Response({'lotes_excluidos': deleted}, status=status.HTTP_200_OK)
