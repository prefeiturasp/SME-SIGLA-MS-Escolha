"""Módulo tests/services/conftest."""

from __future__ import annotations

from uuid import uuid4

import pytest

from escolhas.models import Dre, Escola


@pytest.fixture
@pytest.mark.django_db
def dre_teste():
    """Dre teste."""
    return Dre.objects.create(
        codigo="123456", nome="DRE Teste", sigla="DRE-TESTE"
    )


@pytest.fixture
@pytest.mark.django_db
def escola_1(dre_teste):
    """Escola 1."""
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
@pytest.mark.django_db
def escola_2(dre_teste):
    """Escola 2."""
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
    """Vaga data valida."""
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
    """Vagas data multiplas."""
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
    """Request data valido."""
    return {
        "processo_uuid": str(uuid4()),
        "processo_nome": "Processo Teste",
        "concurso_uuid": str(uuid4()),
        "vagas": vagas_data_multiplas,
    }


@pytest.fixture
def request_data_invalido():
    """Request data invalido."""
    return {
        "vagas": [
            {"data_fechamento_modulo": "2025-09-10", "cargo_codigo": 123}
        ]
    }


@pytest.fixture
def request_data_vazio():
    """Request data vazio."""
    return {"vagas": []}


@pytest.fixture
def concurso_uuid_teste():
    """Concurso uuid teste."""
    return uuid4()


@pytest.fixture
def request_data_com_concurso(vagas_data_multiplas):
    """Request data com concurso."""
    return {
        "processo_uuid": str(uuid4()),
        "processo_nome": "Concurso Professor 2024",
        "vagas": vagas_data_multiplas,
    }


@pytest.fixture
def vaga_data_com_concurso(vaga_data_valida):
    """Vaga data com concurso."""
    return {
        **vaga_data_valida,
        "processo_uuid": str(uuid4()),
        "processo_nome": "Concurso Professor 2024",
    }
