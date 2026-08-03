"""Utilitários compartilhados do projeto."""

from __future__ import annotations

from typing import Any, cast

from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    """Pagina resultados com links, totais e tamanho customizado."""

    page = DEFAULT_PAGE  # type: ignore[assignment]
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"

    def get_paginated_response(self, data: list[Any]) -> Response:
        """Monta resposta JSON com count, page, links e results."""
        page_obj: Any = self.page
        request = cast(Request, self.request)
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": page_obj.paginator.count,
                "page": int(request.GET.get("page", DEFAULT_PAGE)),
                "page_size": int(request.GET.get("page_size", self.page_size)),
                "results": data,
            }
        )
