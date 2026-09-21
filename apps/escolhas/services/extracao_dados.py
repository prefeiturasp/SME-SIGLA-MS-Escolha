"""Agregações para a extração de dados de escolhas."""

from typing import Any
from uuid import UUID

from escolhas.repository import EscolhaRepository
from escolhas.services.candidato_api import CandidatoAPIService


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
        Dicionário com ``concurso_uuid``, ``filtros``
        (quando filtrado por ano), as contagens por situação,
        o array ``dres`` por DRE e ``dres_concursos`` detalhado
        por concurso.
    """
    return EscolhaRepository.montar_extracao_dados(
        concurso_uuid=concurso_uuid, filtros=filtros
    )


def contar_escolhas(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, dict[str, int]]:
    """Conta escolhas por situação, com quebra GERAL/PCD/NNA via MS-Candidatos.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        ano: Ano do filtro (processo ou ``criado_em`` quando sem processo).
        processo_uuids: Processos do ano; quando informados,
            escolhas com vaga são filtradas pelo processo do lote.

    Returns:
        Dicionário por situação com ``total`` e quebra ``geral`` / ``pcd`` /
        ``nna`` (categoria efetiva consultada no MS-Candidatos).
    """
    return EscolhaRepository.contar_escolhas(
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids,
    )


def buscar_categorias_efetivas(
    candidato_uuids: list[str],
) -> dict[str, str]:
    """Consulta no MS-Candidatos a categoria efetiva de cada habilitado.

    Args:
        candidato_uuids: UUIDs de concurso-candidato das escolhas.

    Returns:
        Mapa ``uuid → categoria_efetiva`` (GERAL / PCD / NNA).
        Vazio se a lista for vazia ou a API falhar.
    """
    if not candidato_uuids:
        return {}

    habilitados = CandidatoAPIService().buscar_habilitados_por_uuids(
        candidato_uuids,
        fields=["uuid", "categoria_efetiva"],
    )
    if not habilitados:
        return {}

    return {
        item.get("uuid"): item.get("categoria_efetiva")
        for item in habilitados
    }
