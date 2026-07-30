"""Agregações para a extração de dados de escolhas."""

from typing import Any
from uuid import UUID

from django.db.models import Count, F, Max, Q, QuerySet, Sum

from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha
from vagas_escolas.models import VagasEscolas


def _serializar_datetime(value) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _base_escolhas_com_vaga_qs(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> QuerySet:
    qs = Escolha.objects.filter(
        situacao=SituacaoChoices.ESCOLHA,
        vaga_escola__isnull=False,
    )
    if concurso_uuid:
        qs = qs.filter(concurso_uuid=concurso_uuid)
    if processo_uuids:
        qs = qs.filter(vaga_escola__lote__processo_uuid__in=processo_uuids)
    elif anos:
        qs = qs.filter(criado_em__year__in=anos)
    return qs


def _obter_ultima_escolha_em(
    concurso_uuid: UUID | str | None = None,
    anos: list[int] | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> str | None:
    ultima = _base_escolhas_com_vaga_qs(
        concurso_uuid=concurso_uuid,
        anos=anos,
        processo_uuids=processo_uuids,
    ).aggregate(ultima=Max("criado_em"))["ultima"]
    return _serializar_datetime(ultima)


def _filtrar_escolhas_por_escopo(
    qs: QuerySet,
    *,
    concurso_uuid: UUID | str | None = None,
    ano: int | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> QuerySet:
    """Restringe escolhas ao escopo do filtro de extração.

    Com ``processo_uuids``, alinha ao ano do processo de convocação (como
    candidatos e vagas): escolhas com vaga pelo processo do lote; sem vaga,
    mantém ``criado_em`` no ano do filtro.
    """
    if processo_uuids:
        filtro_com_vaga = Q(
            vaga_escola__lote__processo_uuid__in=processo_uuids
        )
        filtro_sem_vaga = Q(vaga_escola__isnull=True)
        if concurso_uuid:
            filtro_com_vaga &= Q(concurso_uuid=concurso_uuid)
            filtro_sem_vaga &= Q(concurso_uuid=concurso_uuid)
        if ano:
            filtro_sem_vaga &= Q(criado_em__year=ano)
        qs = qs.filter(filtro_com_vaga | filtro_sem_vaga)
    else:
        if concurso_uuid:
            qs = qs.filter(concurso_uuid=concurso_uuid)
        if ano:
            qs = qs.filter(criado_em__year=ano)

    return qs


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
            dados = contar_escolhas(
                concurso_uuid, ano, processo_uuids=processo_uuids
            )
            dados["dres"] = _montar_dres(concurso_uuid, ano, processo_uuids)
            resultado[str(ano)] = dados
        anos = [f["ano"] for f in filtros_ordenados]
    else:
        dados = contar_escolhas(concurso_uuid, ano=None)
        dados["dres"] = _montar_dres(concurso_uuid)
        resultado.update(dados)
        anos = None
        processos_uniao = []

    resultado["dres_concursos"] = _montar_dres_concursos(
        concurso_uuid, anos, processos_uniao
    )
    resultado["ultima_escolha_em"] = _obter_ultima_escolha_em(
        concurso_uuid=concurso_uuid,
        anos=anos,
        processo_uuids=processos_uniao or None,
    )
    return resultado


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
    qs = _filtrar_escolhas_por_escopo(
        Escolha.objects.all(),
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids or None,
    )
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
        ano: Ano do filtro; usado em ``criado_em`` apenas sem processos.
        processo_uuids: Processos do ano para escolhas (via vaga) e vagas.

    Returns:
        Lista de DREs com ``nome``, ``escolhas`` e ``vagas``.
    """
    # escolhas por DRE: somente situacao=escolha (têm vaga_escola)
    escolhas_qs = Escolha.objects.filter(
        situacao=SituacaoChoices.ESCOLHA,
        vaga_escola__isnull=False,
    )
    escolhas_qs = _filtrar_escolhas_por_escopo(
        escolhas_qs,
        concurso_uuid=concurso_uuid,
        ano=ano,
        processo_uuids=processo_uuids or None,
    )
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
        anos: Anos do filtro; usados em ``criado_em`` apenas sem processos.
        processo_uuids: Processos do ano para escolhas (via vaga) e vagas.

    Returns:
        Dicionário por ``concurso_uuid`` com as linhas de DRE e cargo.
    """
    escolhas_qs = Escolha.objects.filter(
        situacao=SituacaoChoices.ESCOLHA,
        vaga_escola__isnull=False,
    )
    if concurso_uuid:
        escolhas_qs = escolhas_qs.filter(concurso_uuid=concurso_uuid)
    if processo_uuids:
        escolhas_qs = escolhas_qs.filter(
            vaga_escola__lote__processo_uuid__in=processo_uuids
        )
    elif anos:
        escolhas_qs = escolhas_qs.filter(criado_em__year__in=anos)

    # escolhas por (concurso, DRE, cargo)
    contagem_qs = escolhas_qs.values(
        "concurso_uuid",
        dre_uuid=F("vaga_escola__escola__dre__uuid"),
        nome=F("vaga_escola__escola__dre__nome"),
        codigo_cargo=F("vaga_escola__cargo_codigo"),
        cargo_descricao=F("vaga_escola__cargo_descricao"),
    ).annotate(
        escolhas=Count("uuid"),
        ultima_escolha_em=Max("criado_em"),
    )

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
            "ultima_escolha_em": _serializar_datetime(
                item["ultima_escolha_em"]
            ),
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
