"""Módulo views/escola."""

from __future__ import annotations

from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from ..models import Escola, Parametrizacao
from ..serializers import EscolaSerializer
from ..utils import CustomPagination


class EscolaViewSet(viewsets.ModelViewSet):
    """ViewSet para o recurso Escola."""

    queryset = Escola.objects.select_related("dre").all()
    serializer_class = EscolaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["dre__codigo"]
    search_fields = ["nome_oficial", "codigo_eol", "nome_dre", "bairro"]
    ordering_fields = ["criado_em", "nome_oficial"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination

    def get_queryset(self) -> Any:
        """Retorna queryset."""
        qs = super().get_queryset()
        tipos_ativos = list(
            Parametrizacao.objects.filter(usar=True).values_list(
                "tipo_ue", flat=True
            )
        )
        if tipos_ativos:
            qs = qs.filter(tipo_ue__in=tipos_ativos)
        else:
            return Escola.objects.none()
        termo = self.request.query_params.get("nome")
        if termo:
            qs = qs.filter(nome_oficial__icontains=termo)
        return qs
