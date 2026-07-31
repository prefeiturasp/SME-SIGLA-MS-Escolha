"""Repositório de acesso a dados de escolas."""

from __future__ import annotations

import logging

from escola.models import Escola

logger = logging.getLogger(__name__)


class EscolaRepository:
    """Acesso aos dados de escolas."""

    @classmethod
    def obter_por_codigo_eol(cls, codigo_eol: str) -> Escola:
        """Busca escola pelo código EOL (modelo para persistência).

        Raises:
            Escola.DoesNotExist: Quando não há escola com o código.
        """
        logger.info(f"Buscando escola pelo código EOL: {codigo_eol}")
        return Escola.objects.get(codigo_eol=codigo_eol)

    @classmethod
    def obter_tipo_ue_por_codigo_eol(cls, codigo_eol: str) -> Escola:
        """Busca escola pelo EOL carregando apenas tipo_ue.

        Raises:
            Escola.DoesNotExist: Quando não há escola com o código.
        """
        logger.info(
            f"Buscando tipo_ue da escola pelo código EOL: {codigo_eol}"
        )
        return Escola.objects.only("tipo_ue").get(codigo_eol=codigo_eol)

    @classmethod
    def listar_tipos_ue_distintos(cls) -> list[str]:
        """Lista tipos de UE distintos cadastrados nas escolas."""
        logger.info("Listando tipos de UE distintos das escolas")
        return list(
            Escola.objects.exclude(tipo_ue__isnull=True)
            .exclude(tipo_ue="")
            .order_by("tipo_ue")
            .values_list("tipo_ue", flat=True)
            .distinct()
        )
