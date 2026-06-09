"""Módulo utils."""

from __future__ import annotations

from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    """Define CustomPagination."""

    page = DEFAULT_PAGE  # type: ignore[assignment]
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"

    def get_paginated_response(self, data: Any) -> Any:
        """Executa get paginated response.

        Args:
            self: Instância do objeto.
            data: Dados de entrada.

        Returns:
            Valor calculado para o campo ou propriedade.

        Raises:
            Nenhuma exceção específica documentada.
        """
        try:
            page = int(self.request.GET.get("page", DEFAULT_PAGE))  # type: ignore[union-attr]
        except (ValueError, TypeError):
            page = DEFAULT_PAGE
        try:
            page_size = int(self.request.GET.get("page_size", self.page_size))  # type: ignore[union-attr]
        except (ValueError, TypeError):
            page_size = self.page_size
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "page": page,
                "page_size": page_size,
                "results": data,
            }
        )  # type: ignore[has-type]
