"""Fixtures compartilhadas entre os apps."""

from __future__ import annotations

import uuid

import pytest
from rest_framework.test import APIClient

from escola.models import Dre, Escola


@pytest.fixture(autouse=True)
def _sem_sigla_sdk_middleware(settings):
    """Remove middlewares do sigla_sdk ausentes no pacote de testes."""
    settings.MIDDLEWARE = [
        middleware
        for middleware in settings.MIDDLEWARE
        if not middleware.startswith("sigla_sdk.middlewares.")
    ]


@pytest.fixture
def api_client():
    """Cliente API sem autenticação."""
    return APIClient()


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
