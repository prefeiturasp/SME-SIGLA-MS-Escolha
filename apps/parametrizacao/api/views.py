"""Módulo views/parametrizacao."""

from __future__ import annotations

from typing import Any

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from parametrizacao.models import Parametrizacao
from parametrizacao.serializers import (
    ParametrizacaoBulkItemSerializer,
    ParametrizacaoSerializer,
)


class ParametrizacaoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Lista e atualiza parametrizações de tipos de UE."""

    queryset = Parametrizacao.objects.all()
    serializer_class = ParametrizacaoSerializer
    permission_classes = [AllowAny]
    lookup_field = "uuid"
    ordering = ["tipo_ue"]
    pagination_class = None

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Rejeita POST com 405 — criação não permitida neste endpoint."""
        return Response(
            {"detail": 'Method "POST" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        methods=["post"],
        detail=False,
        url_path="sync",
        permission_classes=[AllowAny],
    )
    def sync(self, request: Any) -> Any:
        """Cria parametrizações faltantes a partir dos tipo_ue das escolas.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resposta HTTP com a quantidade de registros criados.
        """
        created = Parametrizacao.sync_from_escolas()
        return Response({"created": created})

    @action(
        methods=["patch"],
        detail=False,
        url_path="bulk",
        url_name="bulk",
        permission_classes=[AllowAny],
    )
    def bulk_update(self, request: Any) -> Any:
        """Atualiza em lote o campo usar dos registros informados.

        Args:
            request: Requisição HTTP com lista de {uuid, usar}.

        Returns:
            Resposta HTTP com a quantidade de registros atualizados.
        """
        serializer = ParametrizacaoBulkItemSerializer(
            data=request.data, many=True
        )
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data
        by_uuid = {str(item["uuid"]): bool(item["usar"]) for item in items}
        if not by_uuid:
            return Response({"updated": 0}, status=status.HTTP_200_OK)
        updates = []
        for item in Parametrizacao.objects.filter(
            uuid__in=list(by_uuid.keys())
        ):
            item.usar = by_uuid.get(str(item.uuid), item.usar)
            updates.append(item)
        if not updates:
            return Response({"updated": 0}, status=status.HTTP_200_OK)
        Parametrizacao.objects.bulk_update(updates, ["usar"])
        return Response({"updated": len(updates)}, status=status.HTTP_200_OK)
