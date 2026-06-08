import uuid
from datetime import datetime, timezone

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from escolhas.choices import SituacaoChoices
from escolhas.models import (
    Dre,
    Escola,
    Escolha,
    VagasEscolas,
    VagasEscolasLote,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def _set_ano(escolha, ano):
    """criado_em é auto_now_add; sobrescreve via update() para o ano dado."""
    Escolha.objects.filter(pk=escolha.pk).update(
        criado_em=datetime(ano, 6, 1, tzinfo=timezone.utc)
    )


def criar_escolha(concurso_uuid, situacao, ano, vaga_escola=None):
    escolha = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=concurso_uuid,
        situacao=situacao,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )
    _set_ano(escolha, ano)
    return escolha


def criar_dre(nome):
    return Dre.objects.create(
        codigo=uuid.uuid4().hex[:6], nome=nome, sigla=f"SIG-{nome}"
    )


def criar_escola(dre):
    return Escola.objects.create(
        codigo_eol=uuid.uuid4().hex[:6],
        nome_oficial="Escola",
        dre=dre,
        cep="00000-000",
    )


def criar_vaga(processo_uuid, dre, definitivas, precarias):
    lote = VagasEscolasLote.objects.create(
        processo_uuid=processo_uuid, processo_nome="Processo"
    )
    return VagasEscolas.objects.create(
        escola=criar_escola(dre),
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo",
        vagas_definitivas=definitivas,
        vagas_precarias=precarias,
        status="1",
    )


def test_extracao_dados_conta_situacoes_por_ano(api_client):
    url = reverse("extracao-dados-list")
    concurso_uuid = uuid.uuid4()

    # 2026: 2 escolha, 1 reconvocacao, 1 nao-escolha (todas SEM vaga_escola)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026)
    criar_escolha(concurso_uuid, SituacaoChoices.RECONVOCACAO, 2026)
    criar_escolha(concurso_uuid, SituacaoChoices.NAO_ESCOLHA, 2026)

    # 2025: 1 escolha (mesmo concurso, outro ano)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2025)

    # outro concurso nao deve contar
    criar_escolha(uuid.uuid4(), SituacaoChoices.ESCOLHA, 2026)

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "filtros": [{"ano": 2026}, {"ano": 2025}],
    }

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200, resp.content
    data = resp.json()

    # sem processo_uuids e sem escolhas com vaga -> dres vazio
    assert data["2026"] == {
        "escolha": 2,
        "reconvocacao": 1,
        "nao-escolha": 1,
        "dres": [],
    }
    assert data["2025"] == {
        "escolha": 1,
        "reconvocacao": 0,
        "nao-escolha": 0,
        "dres": [],
    }


def test_extracao_dados_dres_uniao_escolhas_e_vagas(api_client):
    url = reverse("extracao-dados-list")
    concurso_uuid = uuid.uuid4()
    processo = uuid.uuid4()

    dre_a = criar_dre("DRE-A")  # tem escolha E vaga
    dre_b = criar_dre("DRE-B")  # so vaga (sem escolha)
    dre_c = criar_dre("DRE-C")  # so escolha (sem vaga no processo)

    # vagas no processo filtrado
    vaga_a = criar_vaga(processo, dre_a, definitivas=70, precarias=50)  # 120
    criar_vaga(processo, dre_b, definitivas=60, precarias=40)  # 100

    # vaga da DRE-C em OUTRO processo (nao deve contar nas vagas)
    vaga_c_outro = criar_vaga(uuid.uuid4(), dre_c, definitivas=10, precarias=5)

    # escolhas (situacao=escolha) com vaga -> entram em escolhas por DRE
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_a)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_a)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_c_outro)

    # nao-escolha / reconvocacao sem vaga -> NAO entram em dres
    criar_escolha(concurso_uuid, SituacaoChoices.NAO_ESCOLHA, 2026)
    criar_escolha(concurso_uuid, SituacaoChoices.RECONVOCACAO, 2026)

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "filtros": [{"ano": 2026, "processo_uuids": [str(processo)]}],
    }

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200, resp.content
    ano = resp.json()["2026"]

    assert ano["escolha"] == 3
    assert ano["reconvocacao"] == 1
    assert ano["nao-escolha"] == 1

    dres = {d["nome"]: d for d in ano["dres"]}
    assert dres["DRE-A"] == {"nome": "DRE-A", "escolhas": 2, "vagas": 120}
    # DRE-B: so vaga
    assert dres["DRE-B"] == {"nome": "DRE-B", "escolhas": 0, "vagas": 100}
    # DRE-C: so escolha (vaga em outro processo -> vagas 0)
    assert dres["DRE-C"] == {"nome": "DRE-C", "escolhas": 1, "vagas": 0}
    assert set(dres.keys()) == {"DRE-A", "DRE-B", "DRE-C"}


def test_extracao_dados_exige_concurso_uuid(api_client):
    url = reverse("extracao-dados-list")
    resp = api_client.post(url, {"filtros": [{"ano": 2026}]}, format="json")
    assert resp.status_code == 400


def test_extracao_dados_exige_filtros(api_client):
    url = reverse("extracao-dados-list")
    resp = api_client.post(
        url, {"concurso_uuid": str(uuid.uuid4())}, format="json"
    )
    assert resp.status_code == 400
