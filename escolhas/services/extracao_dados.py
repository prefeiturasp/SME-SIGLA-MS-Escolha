"""Agregações para a extração de dados de escolhas."""

from typing import Any
from uuid import UUID

from django.db.models import Count, F, Sum

from escolhas.choices import SituacaoChoices
from escolhas.models import Escolha, VagasEscolas


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
        Dicionário com as contagens por situação, o array ``dres`` por DRE
        e ``dres_concursos`` detalhado por concurso.
    """
    resultado: dict[str, Any] = {}
    if filtros:
        processos_uniao: list = []
        for filtro in filtros:
            ano = filtro["ano"]
            processo_uuids = filtro.get("processo_uuids") or []
            processos_uniao.extend(processo_uuids)
            dados = contar_escolhas(concurso_uuid, ano)
            dados["dres"] = _montar_dres(concurso_uuid, ano, processo_uuids)
            resultado[str(ano)] = dados
        anos = [f["ano"] for f in filtros]
    else:
        dados = contar_escolhas(concurso_uuid, ano=None)
        dados["dres"] = _montar_dres(concurso_uuid)
        resultado.update(dados)
        anos = None
        processos_uniao = []

    resultado["dres_concursos"] = _montar_dres_concursos(
        concurso_uuid, anos, processos_uniao
    )
    return resultado


def contar_escolhas(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
) -> dict[str, int]:
    """Conta escolhas por situação.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        ano: Ano de criação a filtrar; ausente → todos os anos.

    Returns:
        Dicionário com a contagem por ``escolha`` / ``reconvocacao`` /
        ``nao-escolha``.
    """
    qs = Escolha.objects.all()
    if concurso_uuid:
        qs = qs.filter(concurso_uuid=concurso_uuid)
    if ano:
        qs = qs.filter(criado_em__year=ano)
    contagens = qs.values("situacao").annotate(total=Count("uuid"))
    por_situacao: dict[str, int] = {
        item["situacao"]: item["total"] for item in contagens
    }
    return {
        "escolha": por_situacao.get(SituacaoChoices.ESCOLHA, 0),
        "reconvocacao": por_situacao.get(SituacaoChoices.RECONVOCACAO, 0),
        "nao-escolha": por_situacao.get(SituacaoChoices.NAO_ESCOLHA, 0),
    }


def _montar_dres(
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> list[dict[str, Any]]:
    """Une, por DRE, as escolhas realizadas e as vagas ofertadas.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        ano: Ano de criação a filtrar; ausente → todos os anos.
        processo_uuids: Processos a filtrar as vagas; ausente → todas as
            vagas.

    Returns:
        Lista de DREs com ``nome``, ``escolhas`` e ``vagas``.
    """
    # escolhas por DRE: somente situacao=escolha (têm vaga_escola)
    escolhas_qs = Escolha.objects.filter(
        situacao=SituacaoChoices.ESCOLHA,
        vaga_escola__isnull=False,
    )
    if concurso_uuid:
        escolhas_qs = escolhas_qs.filter(concurso_uuid=concurso_uuid)
    if ano:
        escolhas_qs = escolhas_qs.filter(criado_em__year=ano)
    escolhas_qs = escolhas_qs.values(
        dre_uuid=F("vaga_escola__escola__dre__uuid"),
        nome=F("vaga_escola__escola__dre__nome"),
    ).annotate(escolhas=Count("uuid"))

    # vagas por DRE: filtradas pelos processos do filtro; sem filtro, todas
    vagas_qs = VagasEscolas.objects.all()
    if processo_uuids:
        vagas_qs = vagas_qs.filter(lote__processo_uuid__in=processo_uuids)
    vagas_qs = vagas_qs.values(
        dre_uuid=F("escola__dre__uuid"),
        nome=F("escola__dre__nome"),
    ).annotate(vagas=Sum(F("vagas_definitivas") + F("vagas_precarias")))

    # união por DRE (chave = uuid da DRE)
    dres: dict[Any, dict[str, Any]] = {}
    for item in escolhas_qs:
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


def _montar_dres_concursos(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Detalha, por concurso, as escolhas e vagas por DRE e cargo.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        anos: Anos de criação a filtrar; ausente → todos os anos.
        processo_uuids: Processos a filtrar as vagas; ausente → todas as
            vagas.

    Returns:
        Dicionário por ``concurso_uuid`` com as linhas de DRE e cargo.
    """
    escolhas_qs = Escolha.objects.filter(
        situacao=SituacaoChoices.ESCOLHA,
        vaga_escola__isnull=False,
    )
    if concurso_uuid:
        escolhas_qs = escolhas_qs.filter(concurso_uuid=concurso_uuid)
    if anos:
        escolhas_qs = escolhas_qs.filter(criado_em__year__in=anos)

    # escolhas por (concurso, DRE, cargo)
    contagem_qs = escolhas_qs.values(
        "concurso_uuid",
        dre_uuid=F("vaga_escola__escola__dre__uuid"),
        nome=F("vaga_escola__escola__dre__nome"),
        codigo_cargo=F("vaga_escola__cargo_codigo"),
        cargo_descricao=F("vaga_escola__cargo_descricao"),
    ).annotate(escolhas=Count("uuid"))

    # estrutura: { concurso_str: { (dre_uuid, cargo): linha } }
    por_concurso: dict[str, dict[tuple, dict[str, Any]]] = {}
    for item in contagem_qs:
        cuuid = str(item["concurso_uuid"])
        chave = (item["dre_uuid"], item["codigo_cargo"])
        por_concurso.setdefault(cuuid, {})[chave] = {
            "nome": item["nome"],
            "escolhas": item["escolhas"],
            "vagas": 0,
            "codigo_cargo": item["codigo_cargo"],
            "cargo_descricao": item["cargo_descricao"],
        }

    # vagas por (concurso, DRE, cargo) via lote.concurso_uuid (ignora nulos)
    vagas_qs = VagasEscolas.objects.filter(lote__concurso_uuid__isnull=False)
    if processo_uuids:
        vagas_qs = vagas_qs.filter(lote__processo_uuid__in=processo_uuids)
    vagas_qs = vagas_qs.values(
        "cargo_codigo",
        "cargo_descricao",
        concurso=F("lote__concurso_uuid"),
        dre_uuid=F("escola__dre__uuid"),
        nome=F("escola__dre__nome"),
    ).annotate(vagas=Sum(F("vagas_definitivas") + F("vagas_precarias")))

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
