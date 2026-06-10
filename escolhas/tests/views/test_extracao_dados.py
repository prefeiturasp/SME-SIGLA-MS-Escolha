import uuid
from datetime import UTC, datetime

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
        criado_em=datetime(ano, 6, 1, tzinfo=UTC)
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


def criar_vaga(
    processo_uuid,
    dre,
    definitivas,
    precarias,
    cargo_codigo=100,
    cargo_descricao="Cargo",
    concurso_uuid=None,
):
    lote = VagasEscolasLote.objects.create(
        processo_uuid=processo_uuid,
        processo_nome="Processo",
        concurso_uuid=concurso_uuid,
    )
    return VagasEscolas.objects.create(
        escola=criar_escola(dre),
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=cargo_codigo,
        cargo_descricao=cargo_descricao,
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


def test_extracao_dados_sem_filtros_retorna_total(api_client):
    url = reverse("extracao-dados-list")
    concurso_uuid = uuid.uuid4()
    processo = uuid.uuid4()

    dre_a = criar_dre("DRE-A")  # tem escolha E vaga
    dre_b = criar_dre("DRE-B")  # so vaga (sem escolha)

    vaga_a = criar_vaga(processo, dre_a, definitivas=70, precarias=50)  # 120
    criar_vaga(uuid.uuid4(), dre_b, definitivas=60, precarias=40)  # 100

    # escolhas do concurso em anos diferentes -> agregadas no total
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_a)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2025, vaga_a)
    criar_escolha(concurso_uuid, SituacaoChoices.RECONVOCACAO, 2026)
    criar_escolha(concurso_uuid, SituacaoChoices.NAO_ESCOLHA, 2026)

    payload = {"concurso_uuid": str(concurso_uuid)}

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200, resp.content
    data = resp.json()

    # sem quebra por ano: chave "total" + a chave global "dres_concursos"
    assert set(data.keys()) == {"total", "dres_concursos"}
    total = data["total"]
    assert total["escolha"] == 2
    assert total["reconvocacao"] == 1
    assert total["nao-escolha"] == 1

    dres = {d["nome"]: d for d in total["dres"]}
    # DRE-A: 2 escolhas (anos diferentes agregados) + todas as vagas
    assert dres["DRE-A"] == {"nome": "DRE-A", "escolhas": 2, "vagas": 120}
    # DRE-B: so vaga (todas as VagasEscolas entram no agregado)
    assert dres["DRE-B"] == {"nome": "DRE-B", "escolhas": 0, "vagas": 100}
    assert set(dres.keys()) == {"DRE-A", "DRE-B"}


def test_extracao_dados_body_vazio_agrega_tudo(api_client):
    url = reverse("extracao-dados-list")

    # escolhas de concursos diferentes -> todas contam no agregado
    criar_escolha(uuid.uuid4(), SituacaoChoices.ESCOLHA, 2026)
    criar_escolha(uuid.uuid4(), SituacaoChoices.NAO_ESCOLHA, 2025)

    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert set(data.keys()) == {"total", "dres_concursos"}
    assert data["total"]["escolha"] == 1
    assert data["total"]["nao-escolha"] == 1


def test_dres_concursos_por_concurso_dre_e_cargo(api_client):
    url = reverse("extracao-dados-list")
    concurso_uuid = uuid.uuid4()
    processo = uuid.uuid4()

    dre_a = criar_dre("DRE-A")
    dre_b = criar_dre("DRE-B")

    # DRE-A: cargo 1001 (Backend) -> 2 escolhas na MESMA vaga (vagas conta 1x)
    vaga_a1 = criar_vaga(
        processo,
        dre_a,
        70,
        50,
        cargo_codigo=1001,
        cargo_descricao="Backend",
        concurso_uuid=concurso_uuid,
    )  # vagas = 120
    # DRE-B: cargo 1002 (Frontend) -> 1 escolha
    vaga_b2 = criar_vaga(
        processo,
        dre_b,
        60,
        40,
        cargo_codigo=1002,
        cargo_descricao="Frontend",
        concurso_uuid=concurso_uuid,
    )  # vagas = 100
    # DRE-A cargo 1003 (Mobile) -> SO vaga, SEM escolha:
    # vagas vêm do lote.concurso_uuid, então esta linha aparece com escolhas=0.
    criar_vaga(
        processo,
        dre_a,
        5,
        5,
        cargo_codigo=1003,
        cargo_descricao="Mobile",
        concurso_uuid=concurso_uuid,
    )  # vagas = 10

    # escolhas do concurso (situacao=escolha, com vaga)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_a1)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_a1)
    criar_escolha(concurso_uuid, SituacaoChoices.ESCOLHA, 2026, vaga_b2)
    # nao-escolha sem vaga -> nao entra em dres_concursos
    criar_escolha(concurso_uuid, SituacaoChoices.NAO_ESCOLHA, 2026)

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "filtros": [{"ano": 2026, "processo_uuids": [str(processo)]}],
    }

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200, resp.content
    dres_concursos = resp.json()["dres_concursos"]

    # so o concurso informado
    assert set(dres_concursos.keys()) == {str(concurso_uuid)}
    linhas = dres_concursos[str(concurso_uuid)]
    por_chave = {(d["nome"], d["codigo_cargo"]): d for d in linhas}

    # DRE-A + Backend: 2 escolhas, vaga contada 1x (120)
    assert por_chave[("DRE-A", 1001)] == {
        "nome": "DRE-A",
        "escolhas": 2,
        "vagas": 120,
        "codigo_cargo": 1001,
        "cargo_descricao": "Backend",
    }
    # DRE-B + Frontend: 1 escolha, 100 vagas
    assert por_chave[("DRE-B", 1002)] == {
        "nome": "DRE-B",
        "escolhas": 1,
        "vagas": 100,
        "codigo_cargo": 1002,
        "cargo_descricao": "Frontend",
    }
    # DRE-A + Mobile (1003): so vaga (escolhas=0), vinda dos processos
    assert por_chave[("DRE-A", 1003)] == {
        "nome": "DRE-A",
        "escolhas": 0,
        "vagas": 10,
        "codigo_cargo": 1003,
        "cargo_descricao": "Mobile",
    }
    assert set(por_chave.keys()) == {
        ("DRE-A", 1001),
        ("DRE-B", 1002),
        ("DRE-A", 1003),
    }


def test_dres_concursos_vagas_nao_vazam_entre_concursos(api_client):
    """Vagas atribuidas por lote.concurso_uuid. As vagas de um concurso NAO
    podem aparecer no outro concurso."""
    url = reverse("extracao-dados-list")
    concurso_x = uuid.uuid4()
    concurso_y = uuid.uuid4()
    processo_x = uuid.uuid4()
    processo_y = uuid.uuid4()

    dre = criar_dre("DRE-X")

    # concurso_x: cargo 1004 ; concurso_y: cargo 1008 (lote.concurso_uuid)
    vaga_x = criar_vaga(
        processo_x,
        dre,
        30,
        0,
        cargo_codigo=1004,
        cargo_descricao="Infantil",
        concurso_uuid=concurso_x,
    )
    vaga_y = criar_vaga(
        processo_y,
        dre,
        90,
        0,
        cargo_codigo=1008,
        cargo_descricao="Fund",
        concurso_uuid=concurso_y,
    )

    # escolhas em cada concurso
    criar_escolha(concurso_x, SituacaoChoices.ESCOLHA, 2026, vaga_x)
    criar_escolha(concurso_y, SituacaoChoices.ESCOLHA, 2026, vaga_y)

    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == 200, resp.content
    dres_concursos = resp.json()["dres_concursos"]

    assert set(dres_concursos.keys()) == {str(concurso_x), str(concurso_y)}

    # concurso_x: SO cargo 1004 (vagas de 1008 nao vazam)
    cargos_x = {
        linha["codigo_cargo"] for linha in dres_concursos[str(concurso_x)]
    }
    assert cargos_x == {1004}
    linha_x = dres_concursos[str(concurso_x)][0]
    assert linha_x["vagas"] == 30
    assert linha_x["escolhas"] == 1

    # concurso_y: SO cargo 1008
    cargos_y = {
        linha["codigo_cargo"] for linha in dres_concursos[str(concurso_y)]
    }
    assert cargos_y == {1008}
    linha_y = dres_concursos[str(concurso_y)][0]
    assert linha_y["vagas"] == 90
    assert linha_y["escolhas"] == 1


def test_dres_concursos_vaga_sem_escolha_aparece_pelo_lote_concurso(
    api_client,
):
    """Vaga sem nenhuma escolha mas com lote.concurso_uuid -> aparece no
    concurso (escolhas=0). Vaga com lote.concurso_uuid nulo -> ignorada."""
    url = reverse("extracao-dados-list")
    concurso = uuid.uuid4()
    processo_com_escolha = uuid.uuid4()
    processo_sem_escolha = uuid.uuid4()
    processo_legado = uuid.uuid4()

    dre = criar_dre("DRE-X")
    vaga_ok = criar_vaga(
        processo_com_escolha,
        dre,
        20,
        0,
        cargo_codigo=1004,
        cargo_descricao="Infantil",
        concurso_uuid=concurso,
    )
    # vaga SEM escolha, mas com lote.concurso_uuid -> agora aparece
    criar_vaga(
        processo_sem_escolha,
        dre,
        99,
        0,
        cargo_codigo=1008,
        cargo_descricao="Fund",
        concurso_uuid=concurso,
    )
    # vaga com lote.concurso_uuid NULO (legado) -> ignorada
    criar_vaga(
        processo_legado,
        dre,
        7,
        0,
        cargo_codigo=1009,
        cargo_descricao="Legado",
        concurso_uuid=None,
    )

    criar_escolha(concurso, SituacaoChoices.ESCOLHA, 2026, vaga_ok)

    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == 200, resp.content
    dres_concursos = resp.json()["dres_concursos"]

    assert set(dres_concursos.keys()) == {str(concurso)}
    por_cargo = {
        linha["codigo_cargo"]: linha for linha in dres_concursos[str(concurso)]
    }
    # cargo 1008 (vaga sem escolha) APARECE com escolhas=0
    assert por_cargo[1008]["escolhas"] == 0
    assert por_cargo[1008]["vagas"] == 99
    # cargo 1004 com escolha
    assert por_cargo[1004]["escolhas"] == 1
    assert por_cargo[1004]["vagas"] == 20
    # cargo 1009 (lote sem concurso_uuid) NAO aparece
    assert set(por_cargo.keys()) == {1004, 1008}


def test_dres_concursos_concurso_so_com_vaga_aparece(api_client):
    """Concurso que so tem vagas (nenhuma escolha) aparece na uniao."""
    url = reverse("extracao-dados-list")
    concurso_com_escolha = uuid.uuid4()
    concurso_so_vaga = uuid.uuid4()
    processo_a = uuid.uuid4()
    processo_b = uuid.uuid4()

    dre = criar_dre("DRE-X")
    vaga_a = criar_vaga(
        processo_a,
        dre,
        10,
        0,
        cargo_codigo=1004,
        cargo_descricao="Infantil",
        concurso_uuid=concurso_com_escolha,
    )
    criar_vaga(
        processo_b,
        dre,
        50,
        0,
        cargo_codigo=1008,
        cargo_descricao="Fund",
        concurso_uuid=concurso_so_vaga,
    )

    # so o primeiro concurso tem escolha
    criar_escolha(concurso_com_escolha, SituacaoChoices.ESCOLHA, 2026, vaga_a)

    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == 200, resp.content
    dres_concursos = resp.json()["dres_concursos"]

    # uniao: ambos os concursos aparecem
    assert set(dres_concursos.keys()) == {
        str(concurso_com_escolha),
        str(concurso_so_vaga),
    }
    # concurso so-com-vaga: linha com escolhas=0
    linha = dres_concursos[str(concurso_so_vaga)][0]
    assert linha["escolhas"] == 0
    assert linha["vagas"] == 50
    assert linha["codigo_cargo"] == 1008
