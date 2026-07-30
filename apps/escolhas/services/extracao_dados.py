"""Agregações para a extração de dados de escolhas."""

from typing import Any
from uuid import UUID

from escolhas.repository import EscolhaRepository


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    filtros: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de indicadores de escolhas.

    Delega ao repositório (padrão alinhado ao ms-processos-concursos).
    """
    return EscolhaRepository.montar_extracao_dados(
        concurso_uuid=concurso_uuid, filtros=filtros
    )


def contar_escolhas(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, int]:
    """Conta escolhas por situação."""
    return EscolhaRepository.contar_escolhas(
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids,
    )
