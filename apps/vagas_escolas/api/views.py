"""Módulo views/vagas_escolas."""

from __future__ import annotations

import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from escolhas.middleware import get_correlation_id
from vagas_escolas.models import VagasEscolas
from vagas_escolas.repository import VagasEscolasRepository
from vagas_escolas.serializers import (
    VagaEscolaUtilizadaItemSerializer,
    VagasEscolasSerializer,
)
from vagas_escolas.services import processar_criacao_vagas_lote
from vagas_escolas.services.exceptions import TipoUEDesabilitadoException
from vagas_escolas.services.vagas_escolas import (
    adicionar_vagas_ao_lote_por_processo,
    atualizar_vagas_utilizadas_por_processo,
)

logger = logging.getLogger(__name__)


class VagasEscolasViewSet(ModelViewSet):
    """Gerencia vagas por processo, cargo e escola."""

    queryset = VagasEscolas.objects.select_related(
        "escola", "escola__dre", "lote"
    ).all()
    serializer_class = VagasEscolasSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "escola__codigo_eol",
        "escola__dre__codigo",
        "cargo_codigo",
    ]

    def get_queryset(self) -> Any:
        """Restringe vagas ao lote mais recente do processo_uuid."""
        qs = super().get_queryset()
        processo_uuid = self.request.query_params.get("processo_uuid")
        if processo_uuid:
            lote = (
                VagasEscolasRepository.obter_lote_mais_recente_por_processo(
                    processo_uuid
                )
            )
            if not lote:
                return VagasEscolas.objects.none()
            qs = qs.filter(lote=lote)
        return qs

    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Lista vagas checadas com totais agregados e DREs."""
        logger.info(
            "Listando vagas das escolas",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "user": request.user,
            },
        )
        qs = self.filter_queryset(self.get_queryset())
        return Response(VagasEscolasRepository.montar_listagem(qs))

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Cria vagas das escolas em lote."""
        logger.info(
            "Criando vagas das escolas em lote",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "processo_uuid": request.data.get("processo_uuid"),
                "processo_nome": request.data.get("processo_nome"),
                "vagas": len(request.data.get("vagas", [])),
                "user": request.user,
            },
        )
        try:
            response_data, status_code = processar_criacao_vagas_lote(
                request.data
            )
            return Response(response_data, status=status_code)
        except TipoUEDesabilitadoException as exc:
            msg = str(exc)
            logger.error(f"Tipo UE desabilitado: {msg}")
            return Response(
                {"detail": msg, "code": "TIPO_UE_DESABILITADO"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            msg = str(exc)
            logger.error(f"Erro ao criar vagas em lote: {msg}")
            return Response(
                {"detail": msg, "code": "ERRO_AO_CRIAR_VAGAS_EM_LOTE"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["patch"], url_path="utilizadas")
    def utilizadas(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Atualiza vagas utilizadas e flags de checagem em lote."""
        logger.info(
            "Atualizando vagas utilizadas",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "data": request.data,
                "user": request.user,
            },
        )
        payload = VagaEscolaUtilizadaItemSerializer(
            data=request.data, many=True
        )
        payload.is_valid(raise_exception=True)
        vagas = payload.validated_data
        result = atualizar_vagas_utilizadas_por_processo(vagas)
        return Response(result)

    @action(detail=False, methods=["post"], url_path="inclusao")
    def atualizar_vagas_lote(
        self, request: Any, *args: Any, **kwargs: Any
    ) -> Any:
        """Adiciona novas vagas ao lote do processo informado."""
        response_data, status_code = adicionar_vagas_ao_lote_por_processo(
            request.data
        )
        return Response(response_data, status=status_code)

    @action(detail=False, methods=["get"], url_path="por-cargo-e-escolas")
    def por_cargo_e_escolas(
        self, request: Any, *args: Any, **kwargs: Any
    ) -> Any:
        """Filtra vagas por cargo_codigo e/ou códigos EOL."""
        logger.info(
            "Buscando vagas por cargo e escolas",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "user": request.user,
                "params": request.query_params,
            },
        )
        codigo_cargo = request.query_params.get("cargo_codigo")
        eols = request.query_params.getlist("codigo_eol") or (
            request.query_params.get("codigo_eol__in", "").split(",")
            if request.query_params.get("codigo_eol__in")
            else []
        )
        data = VagasEscolasRepository.listar_por_cargo_e_eols(
            cargo_codigo=codigo_cargo, eols=eols or None
        )
        return Response(data)

    @action(detail=False, methods=["delete"], url_path="por-processo")
    def excluir_por_processo(self, request: Any) -> Any:
        """Remove lotes de vagas (e vagas em cascata) do processo informado."""
        processo_uuid = request.query_params.get("processo_uuid")
        if not processo_uuid:
            return Response(
                {"detail": "processo_uuid é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted = VagasEscolasRepository.excluir_lotes_por_processo(
            processo_uuid
        )
        logger.info(
            "Lotes de vagas excluídos por processo",
            extra={
                "correlation_id": get_correlation_id(),
                "processo_uuid": processo_uuid,
                "lotes_excluidos": deleted,
            },
        )
        return Response(
            {"lotes_excluidos": deleted}, status=status.HTTP_200_OK
        )
