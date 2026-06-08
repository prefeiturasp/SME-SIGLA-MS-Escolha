"""Agregações para a extração de dados de escolhas."""

from django.db.models import Count, F, Sum

from escolhas.choices import SituacaoChoices
from escolhas.models import Escolha, VagasEscolas


def montar_extracao_dados(concurso_uuid, filtros) -> dict:
    """
    Monta o dicionário de indicadores de escolhas por ano.

    Para cada ``ano`` (de ``filtros``), conta as escolhas do ``concurso_uuid``
    por ``situacao`` (escolha / reconvocacao / nao-escolha), filtrando pelo
    ano de criação (``criado_em``), e monta o array ``dres`` com escolhas e
    vagas por DRE.

    Filtramos por ``Escolha.concurso_uuid`` (sempre preenchido) e NÃO pela
    vaga, porque escolhas ``nao-escolha`` / ``reconvocacao`` normalmente não
    têm ``vaga_escola`` vinculada — filtrar pela vaga as excluiria.
    """
    resultado = {}
    for filtro in filtros:
        ano = filtro["ano"]
        processo_uuids = filtro.get("processo_uuids") or []
        dados = _contar_situacoes(concurso_uuid, ano)
        dados["dres"] = _montar_dres(concurso_uuid, ano, processo_uuids)
        resultado[str(ano)] = dados
    return resultado


def _contar_situacoes(concurso_uuid, ano) -> dict:
    contagens = (
        Escolha.objects.filter(
            concurso_uuid=concurso_uuid, criado_em__year=ano
        )
        .values("situacao")
        .annotate(total=Count("uuid"))
    )
    por_situacao = {item["situacao"]: item["total"] for item in contagens}
    return {
        "escolha": por_situacao.get(SituacaoChoices.ESCOLHA, 0),
        "reconvocacao": por_situacao.get(SituacaoChoices.RECONVOCACAO, 0),
        "nao-escolha": por_situacao.get(SituacaoChoices.NAO_ESCOLHA, 0),
    }


def _montar_dres(concurso_uuid, ano, processo_uuids) -> list:
    """
    Une, por DRE, as escolhas realizadas (situacao=escolha, com vaga) e as
    vagas ofertadas (definitivas + precarias) dos processos informados.

    DRE só com escolha -> vagas=0; DRE só com vaga -> escolhas=0.
    Nome da DRE = ``Dre.nome``.
    """
    # escolhas por DRE: somente situacao=escolha (têm vaga_escola)
    escolhas_qs = (
        Escolha.objects.filter(
            concurso_uuid=concurso_uuid,
            criado_em__year=ano,
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        .values(
            dre_uuid=F("vaga_escola__escola__dre__uuid"),
            nome=F("vaga_escola__escola__dre__nome"),
        )
        .annotate(escolhas=Count("uuid"))
    )

    # vagas por DRE: VagasEscolas filtradas pelos processos do filtro
    vagas_qs = (
        VagasEscolas.objects.filter(lote__processo_uuid__in=processo_uuids)
        .values(
            dre_uuid=F("escola__dre__uuid"),
            nome=F("escola__dre__nome"),
        )
        .annotate(vagas=Sum(F("vagas_definitivas") + F("vagas_precarias")))
    )

    # união por DRE (chave = uuid da DRE)
    dres: dict = {}
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
