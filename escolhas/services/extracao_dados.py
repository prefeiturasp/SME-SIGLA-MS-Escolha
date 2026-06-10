"""Agregações para a extração de dados de escolhas."""

from typing import Any, Optional, Union
from uuid import UUID

from django.db.models import Count, F, Sum

from escolhas.choices import SituacaoChoices
from escolhas.models import Escolha, VagasEscolas


def montar_extracao_dados(
    concurso_uuid: Optional[Union[UUID, str]] = None,
    filtros: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """
    Monta o dicionário de indicadores de escolhas.

    - Com ``filtros``: para cada ``ano`` (de ``filtros``), conta as escolhas do
      ``concurso_uuid`` por ``situacao`` (escolha / reconvocacao / nao-escolha),
      filtrando pelo ano de criação (``criado_em``), e monta o array ``dres``
      com escolhas e vagas por DRE (vagas dos ``processo_uuids`` do ano).
    - Sem ``filtros`` (None ou lista vazia): retorna uma única chave ``total``
      agregando as escolhas (de ``concurso_uuid`` se informado, senão de todos
      os concursos) e, em ``dres``, todas as ``VagasEscolas`` por DRE.

    Filtramos por ``Escolha.concurso_uuid`` (sempre preenchido) e NÃO pela
    vaga, porque escolhas ``nao-escolha`` / ``reconvocacao`` normalmente não
    têm ``vaga_escola`` vinculada — filtrar pela vaga as excluiria.
    """
    if filtros:
        resultado: dict[str, Any] = {}
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
        resultado = {"total": dados}
        anos = None
        processos_uniao = []

    resultado["dres_concursos"] = _montar_dres_concursos(
        concurso_uuid, anos, processos_uniao
    )
    return resultado


def contar_escolhas(
    concurso_uuid: Optional[Union[UUID, str]] = None,
    ano: Optional[int] = None,
) -> dict[str, int]:
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
    concurso_uuid: Optional[Union[UUID, str]] = None,
    ano: Optional[int] = None,
    processo_uuids: Optional[list[Union[UUID, str]]] = None,
) -> list[dict[str, Any]]:
    """
    Une, por DRE, as escolhas realizadas (situacao=escolha, com vaga) e as
    vagas ofertadas (definitivas + precarias).

    - ``concurso_uuid`` / ``ano`` filtram as escolhas quando informados.
    - ``processo_uuids`` filtra as vagas quando informado; sem ele (modo
      agregado), soma todas as ``VagasEscolas``.

    DRE só com escolha -> vagas=0; DRE só com vaga -> escolhas=0.
    Nome da DRE = ``Dre.nome``.
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
    concurso_uuid: Optional[Union[UUID, str]] = None,
    anos: Optional[list[int]] = None,
    processo_uuids: Optional[list[Union[UUID, str]]] = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Detalha, por concurso, as escolhas e vagas por DRE + cargo.

    - Chaves do dict = ``concurso_uuid``. União dos concursos presentes nas
      escolhas E nas vagas (``VagasEscolasLote.concurso_uuid``): um concurso só
      com vagas (sem escolha) também aparece.
    - Linha = ``(DRE, codigo_cargo)`` com ``nome`` (Dre.nome), ``escolhas``,
      ``vagas``, ``codigo_cargo``, ``cargo_descricao``.
    - Escolhas: somente ``situacao=escolha`` com vaga (cargo vem da vaga);
      ``anos`` (se informado) filtra por ``criado_em__year``.
    - Vagas: atribuídas direto ao concurso via ``VagasEscolas.lote.concurso_uuid``
      (não vazam entre concursos). Vagas cujo ``lote.concurso_uuid`` é nulo
      (lotes legados) são ignoradas. Combinação DRE+cargo só com vaga aparece
      com ``escolhas=0``.
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
        cuuid: list(linhas.values())
        for cuuid, linhas in por_concurso.items()
    }
