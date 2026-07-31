"""Agregações para a extração de dados de escolhas."""

from typing import Any
from uuid import UUID

from escolhas.repository import EscolhaRepository


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    filtros: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de indicadores de escolhas.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        filtros: Lista de ``{ano, processo_uuids}``; ausente (ou vazia) →
            agregado direto na raiz, sem quebra por ano.

    Returns:
        Dicionário com ``concurso_uuid``, ``filtros`` (quando filtrado por ano),
        as contagens por situação, o array ``dres`` por DRE
        e ``dres_concursos`` detalhado por concurso.
    """
    return EscolhaRepository.montar_extracao_dados(
        concurso_uuid=concurso_uuid, filtros=filtros
    )


def contar_escolhas(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, int]:
    """Conta escolhas por situação.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        ano: Ano do filtro (processo ou ``criado_em`` quando sem processo).
        processo_uuids: Processos do ano; quando informados, escolhas com vaga
            são filtradas pelo processo do lote.

    Returns:
        Dicionário com a contagem por ``escolha`` / ``reconvocacao`` /
        ``nao-escolha``.
    """
    return EscolhaRepository.contar_escolhas(
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids,
    )
