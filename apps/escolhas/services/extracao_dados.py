"""Agregações para a extração de dados de escolhas.

O service orquestra: busca no repository, consulta MS-Candidatos e monta
a resposta final com contagens por situação/categoria e DREs.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from escolhas.constants import CategoriaEfetivaChoices, SituacaoChoices
from escolhas.repository import EscolhaRepository
from escolhas.services.candidato_api import CandidatoAPIService
from vagas_escolas.repository import VagasEscolasRepository

logger = logging.getLogger(__name__)


def _bloco_contagem_vazio() -> dict[str, int]:
    return {"total": 0, "geral": 0, "pcd": 0, "nna": 0}


def _montar_filtros_resposta(
    filtros: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "ano": filtro["ano"],
            "processo_uuids": [
                str(processo_uuid)
                for processo_uuid in (filtro.get("processo_uuids") or [])
            ],
        }
        for filtro in sorted(filtros, key=lambda item: item["ano"])
    ]


def buscar_categorias_efetivas(
    candidato_uuids: list[str],
) -> dict[str, str]:
    """Consulta no MS-Candidatos a categoria efetiva de cada habilitado.

    Args:
        candidato_uuids: UUIDs dos candidatos das escolhas.

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
        str(item.get("uuid")): item.get("categoria_efetiva")
        for item in habilitados
        if item.get("uuid") and item.get("categoria_efetiva")
    }


def contar_escolhas_por_situacao_e_categoria(
    escolhas: list[dict[str, Any]],
    categorias_por_uuid: dict[str, str],
) -> dict[str, dict[str, int]]:
    """Conta escolhas por situação cruzando com categoria efetiva.

    Args:
        escolhas: Lista de ``{candidato_uuid, situacao}``.
        categorias_por_uuid: Mapa uuid → GERAL/PCD/NNA.

    Returns:
        Dicionário por situação com ``total`` / ``geral`` / ``pcd`` / ``nna``.
    """
    resultado = {
        situacao: _bloco_contagem_vazio()
        for situacao in SituacaoChoices.values
    }
    for escolha in escolhas:
        situacao = escolha.get("situacao")
        if situacao not in resultado:
            continue
        resultado[situacao]["total"] += 1
        candidato_uuid = escolha.get("candidato_uuid")
        if not candidato_uuid:
            continue
        categoria = categorias_por_uuid.get(str(candidato_uuid))
        if not categoria or categoria not in CategoriaEfetivaChoices.values:
            continue
        resultado[situacao][categoria.lower()] += 1
    return resultado


def contar_escolhas(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, dict[str, int]]:
    """Busca escolhas no escopo, consulta categorias e monta contagens.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        ano: Ano do filtro (processo ou ``criado_em`` quando sem processo).
        processo_uuids: Processos do ano.

    Returns:
        Contagens por situação com ``total`` / ``geral`` / ``pcd`` / ``nna``.
    """
    escolhas = EscolhaRepository.buscar_escolhas_por_escopo(
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids,
    )
    candidato_uuids = sorted(
        {
            str(item["candidato_uuid"])
            for item in escolhas
            if item.get("candidato_uuid")
        }
    )
    categorias_por_uuid = buscar_categorias_efetivas(candidato_uuids)
    return contar_escolhas_por_situacao_e_categoria(
        escolhas, categorias_por_uuid
    )


def montar_dres(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> list[dict[str, Any]]:
    """Une, por DRE, as escolhas realizadas e as vagas ofertadas."""
    escolhas_por_dre = EscolhaRepository.agregar_escolhas_por_dre(
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids,
    )
    vagas_qs = VagasEscolasRepository.agregar_vagas_por_dre(processo_uuids)

    dres: dict[Any, dict[str, Any]] = {}
    for item in escolhas_por_dre:
        dres[item["dre_uuid"]] = {
            "nome": item["nome"],
            "escolhas": item["escolhas"],
            "vagas": 0,
        }
    for item in vagas_qs:
        entrada = dres.setdefault(
            item["dre_uuid"],
            {"nome": item["nome"], "escolhas": 0, "vagas": 0},
        )
        entrada["vagas"] = item["vagas"] or 0
    return list(dres.values())


def montar_dres_concursos(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Detalha, por concurso, as escolhas e vagas por DRE e cargo."""
    escolhas_qs = EscolhaRepository.agregar_escolhas_por_concurso_dre_cargo(
        concurso_uuid=concurso_uuid,
        anos=anos,
        processo_uuids=processo_uuids,
    )

    por_concurso: dict[str, dict[tuple, dict[str, Any]]] = {}
    for item in escolhas_qs:
        cuuid = str(item["concurso_uuid"])
        chave = (item["dre_uuid"], item["codigo_cargo"])
        por_concurso.setdefault(cuuid, {})[chave] = {
            "nome": item["nome"],
            "escolhas": item["escolhas"],
            "vagas": 0,
            "codigo_cargo": item["codigo_cargo"],
            "cargo_descricao": item["cargo_descricao"],
            "ultima_escolha_em": item["ultima_escolha_em"],
        }

    vagas_qs = VagasEscolasRepository.agregar_vagas_por_concurso_dre_cargo(
        processo_uuids
    )
    for vaga in vagas_qs:
        cuuid = str(vaga["concurso"])
        chave = (vaga["dre_uuid"], vaga["cargo_codigo"])
        linha = por_concurso.setdefault(cuuid, {}).setdefault(
            chave,
            {
                "nome": vaga["nome"],
                "escolhas": 0,
                "vagas": 0,
                "codigo_cargo": vaga["cargo_codigo"],
                "cargo_descricao": vaga["cargo_descricao"],
            },
        )
        linha["vagas"] += vaga["vagas"] or 0

    return {
        cuuid: list(linhas.values()) for cuuid, linhas in por_concurso.items()
    }


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    filtros: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Orquestra a extração: escolhas, categorias, contagens, DREs.

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
    logger.info(
        f"Montando extração de dados: concurso_uuid={concurso_uuid}, "
        f"filtros={filtros}"
    )
    resultado: dict[str, Any] = {}
    if filtros:
        filtros_ordenados = sorted(filtros, key=lambda item: item["ano"])
        if concurso_uuid:
            resultado["concurso_uuid"] = str(concurso_uuid)
        resultado["filtros"] = _montar_filtros_resposta(filtros_ordenados)

        processos_uniao: list = []
        for filtro in filtros_ordenados:
            ano = filtro["ano"]
            processo_uuids = filtro.get("processo_uuids") or []
            processos_uniao.extend(processo_uuids)
            resultado[str(ano)] = {
                **contar_escolhas(
                    concurso_uuid, ano, processo_uuids=processo_uuids
                ),
                "dres": montar_dres(concurso_uuid, ano, processo_uuids),
            }
        anos = [f["ano"] for f in filtros_ordenados]
    else:
        resultado.update(
            {
                **contar_escolhas(concurso_uuid, ano=None),
                "dres": montar_dres(concurso_uuid),
            }
        )
        anos = None
        processos_uniao = []

    resultado["dres_concursos"] = montar_dres_concursos(
        concurso_uuid, anos, processos_uniao
    )
    resultado["ultima_escolha_em"] = EscolhaRepository.obter_ultima_escolha_em(
        concurso_uuid=concurso_uuid,
        anos=anos,
        processo_uuids=processos_uniao or None,
    )
    return resultado
