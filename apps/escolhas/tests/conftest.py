"""Fixtures do app escolhas."""

from __future__ import annotations

import uuid

import pytest

import escolhas.signals  # noqa: F401
from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import (
    Dre,
    Escola,
    Escolha,
    VagasEscolas,
    VagasEscolasLote,
)


@pytest.fixture
def dre():
    """Fixture para criar uma DRE."""
    return Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")


@pytest.fixture
def escola(dre):
    """Fixture para criar uma escola."""
    return Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )


@pytest.fixture
def lote():
    """Fixture para criar um lote de vagas."""
    return VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Processo Teste"
    )


@pytest.fixture
def vaga_escola(escola, lote):
    """Fixture para criar uma vaga de escola."""
    return VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo Teste",
        vagas_precarias=3,
        vagas_precarias_restantes=3,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )


def _criar_escolha(**override):
    """Criar escolha."""
    if "vaga_escola_uuid" in override:
        vaga_uuid = override.pop("vaga_escola_uuid")
        if vaga_uuid:
            try:
                override["vaga_escola"] = VagasEscolas.objects.get(
                    uuid=vaga_uuid
                )
            except VagasEscolas.DoesNotExist:
                dre = Dre.objects.create(
                    codigo="99", nome="DRE Teste", sigla="DRE-TESTE"
                )
                escola = Escola.objects.create(
                    codigo_eol="999999",
                    nome_oficial="Escola Teste",
                    dre=dre,
                    cep="00000-000",
                )
                lote = VagasEscolasLote.objects.create(
                    processo_uuid=uuid.uuid4(), processo_nome="Processo Teste"
                )
                override["vaga_escola"] = VagasEscolas.objects.create(
                    escola=escola,
                    lote=lote,
                    data_fechamento_modulo="2025-01-01",
                    cargo_codigo=100,
                    cargo_descricao="Cargo Teste",
                    vagas_precarias=3,
                    vagas_precarias_restantes=3,
                    vagas_definitivas=5,
                    vagas_definitivas_restantes=5,
                    status="1",
                )
    if "vaga_escola" not in override:
        dre = Dre.objects.create(
            codigo="99", nome="DRE Teste", sigla="DRE-TESTE"
        )
        escola = Escola.objects.create(
            codigo_eol="999999",
            nome_oficial="Escola Teste",
            dre=dre,
            cep="00000-000",
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(), processo_nome="Processo Teste"
        )
        override["vaga_escola"] = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=100,
            cargo_descricao="Cargo Teste",
            vagas_precarias=3,
            vagas_precarias_restantes=3,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1",
        )
    dados = {
        "candidato_uuid": uuid.uuid4(),
        "concurso_uuid": uuid.uuid4(),
        "situacao": SituacaoChoices.ESCOLHA,
        "tipo_vaga": TipoVagaChoices.DEFINITIVA,
        "e_retardatario": False,
    }
    dados.update(override)
    return Escolha.objects.create(**dados)


@pytest.fixture
def escolha_matematica():
    """Fixture para criar uma escolha de matemática."""
    return _criar_escolha()


@pytest.fixture
def escolha_portugues():
    """Fixture para criar uma escolha de português."""
    return _criar_escolha()


@pytest.fixture
def escolha_historia():
    """Fixture para criar uma escolha de história."""
    return _criar_escolha()


@pytest.fixture
def escolha_ciencias():
    """Fixture para criar uma escolha de ciências."""
    return _criar_escolha()


@pytest.fixture
def escolhas_multiplas(
    escolha_matematica, escolha_portugues, escolha_historia, escolha_ciencias
):
    """Fixture para criar múltiplas escolhas de teste."""
    return {
        "matematica": escolha_matematica,
        "portugues": escolha_portugues,
        "historia": escolha_historia,
        "ciencias": escolha_ciencias,
    }


@pytest.fixture
def escolha_data(vaga_escola):
    """Fixture para dados de escolha válidos."""
    return {
        "candidato_uuid": str(uuid.uuid4()),
        "concurso_uuid": str(uuid.uuid4()),
        "situacao": SituacaoChoices.ESCOLHA,
        "tipo_vaga": TipoVagaChoices.DEFINITIVA,
        "e_retardatario": False,
        "vaga_escola_uuid": str(vaga_escola.uuid),
    }


@pytest.fixture
def escolha_data_invalid():
    """Fixture para dados de escolha inválidos."""
    return {
        "candidato_uuid": None,
        "situacao": "invalida",
        "tipo_vaga": "invalida",
        "vaga_escola_uuid": None,
    }


@pytest.fixture
def escolha_data_long_name():
    """Fixture para dados inválidos com valores fora das choices."""
    return {
        "candidato_uuid": str(uuid.uuid4()),
        "situacao": "muito-longa-para-choice",
        "tipo_vaga": "muito-longa-para-choice",
        "e_retardatario": False,
        "vaga_escola_uuid": str(uuid.uuid4()),
    }


@pytest.fixture
def escolha_data_updated():
    """Fixture para dados de escolha atualizados."""
    return {
        "candidato_uuid": str(uuid.uuid4()),
        "concurso_uuid": str(uuid.uuid4()),
        "situacao": SituacaoChoices.RECONVOCACAO,
        "tipo_vaga": TipoVagaChoices.PRECARIA,
        "e_retardatario": True,
    }


@pytest.fixture
def multiple_escolhas():
    """Fixture para criar múltiplas escolhas para testes de paginação."""
    escolhas = []
    for _ in range(25):
        escolha = _criar_escolha()
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def escolhas_ordenadas():
    """Fixture para criar escolhas com situações específicas para teste de."""
    escolhas = []
    situacoes = [
        SituacaoChoices.ESCOLHA,
        SituacaoChoices.NAO_ESCOLHA,
        SituacaoChoices.RECONVOCACAO,
    ]
    for situacao in situacoes:
        escolha = _criar_escolha(situacao=situacao)
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def escolhas_para_busca():
    """Fixture para criar escolhas específicas para teste de busca."""
    escolhas = []
    situacoes = [
        SituacaoChoices.ESCOLHA,
        SituacaoChoices.NAO_ESCOLHA,
        SituacaoChoices.RECONVOCACAO,
    ]
    for situacao in situacoes:
        escolha = _criar_escolha(situacao=situacao)
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def dre_teste():
    """DRE usada nos testes de services/views de vagas e escolas."""
    return Dre.objects.create(
        codigo="123456", nome="DRE Teste", sigla="DRE-TESTE"
    )


@pytest.fixture
def escola_1(dre_teste):
    """Escola 1 para testes de vagas e views."""
    return Escola.objects.create(
        dre=dre_teste,
        codigo_eol="123456",
        nome_oficial="Escola Teste",
        nome_nao_oficial="Escola Teste",
        tipo_unidade_admin="EMEF",
        tipo_ue="EMEF",
        logradouro="Rua Teste",
        numero="123",
        bairro="Bairro Teste",
        cep=12345678,
        distrito="Distrito Teste",
        sub_prefeitura="Subprefeitura Teste",
        nome_dre="DRE Teste",
        status="ativo",
    )


@pytest.fixture
def escola_2(dre_teste):
    """Escola 2 para testes de vagas e views."""
    return Escola.objects.create(
        dre=dre_teste,
        codigo_eol="789012",
        nome_oficial="Escola Teste 2",
        nome_nao_oficial="Escola Teste 2",
        tipo_unidade_admin="EMEF",
        tipo_ue="EMEF",
        logradouro="Rua Teste 2",
        numero="456",
        bairro="Bairro Teste 2",
        cep=12345678,
        distrito="Distrito Teste",
        sub_prefeitura="Subprefeitura Teste",
        nome_dre="DRE Teste",
        status="ativo",
    )


@pytest.fixture
def vaga_data_valida():
    """Payload válido de uma vaga."""
    return {
        "data_fechamento_modulo": "2025-09-10",
        "cargo_codigo": 123,
        "cargo_descricao": "Professor de Matemática",
        "codigo_eol": "123456",
        "vagas_precarias": 2,
        "vagas_definitivas": 3,
        "status": "ativo",
    }


@pytest.fixture
def vagas_data_multiplas():
    """Lista de payloads de vagas."""
    return [
        {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": "123456",
            "vagas_precarias": 2,
            "vagas_definitivas": 3,
            "status": "ativo",
        },
        {
            "data_fechamento_modulo": "2025-09-15",
            "cargo_codigo": 456,
            "cargo_descricao": "Professor de Português",
            "codigo_eol": "789012",
            "vagas_precarias": 1,
            "vagas_definitivas": 2,
            "status": "ativo",
        },
    ]


@pytest.fixture
def request_data_valido(vagas_data_multiplas):
    """Request válido de criação de vagas em lote."""
    return {
        "processo_uuid": str(uuid.uuid4()),
        "processo_nome": "Processo Teste",
        "concurso_uuid": str(uuid.uuid4()),
        "vagas": vagas_data_multiplas,
    }


@pytest.fixture
def request_data_invalido():
    """Request inválido de criação de vagas."""
    return {
        "vagas": [
            {"data_fechamento_modulo": "2025-09-10", "cargo_codigo": 123}
        ]
    }


@pytest.fixture
def request_data_vazio():
    """Request com lista de vagas vazia."""
    return {"vagas": []}


@pytest.fixture
def concurso_uuid_teste():
    """UUID de concurso para testes."""
    return uuid.uuid4()


@pytest.fixture
def request_data_com_concurso(vagas_data_multiplas):
    """Request de vagas com nome de concurso."""
    return {
        "processo_uuid": str(uuid.uuid4()),
        "processo_nome": "Concurso Professor 2024",
        "vagas": vagas_data_multiplas,
    }


@pytest.fixture
def vaga_data_com_concurso(vaga_data_valida):
    """Payload de vaga com dados de processo/concurso."""
    return {
        **vaga_data_valida,
        "processo_uuid": str(uuid.uuid4()),
        "processo_nome": "Concurso Professor 2024",
    }
