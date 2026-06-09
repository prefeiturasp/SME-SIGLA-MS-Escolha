"""Módulo tests/views/conftest."""
from __future__ import annotations
from typing import Any
import pytest
from escolhas.models import Dre, Escola
pytestmark = pytest.mark.django_db

@pytest.fixture
def dre_teste() -> Any:
    """Executa dre teste."""
    return Dre.objects.create(codigo='123456', nome='DRE Teste', sigla='DRE-T')

@pytest.fixture
def escola_1(dre_teste: Any) -> Any:
    """Executa escola 1."""
    return Escola.objects.create(dre=dre_teste, codigo_eol='123456', nome_oficial='Escola 1', nome_nao_oficial='Escola 1', tipo_unidade_admin='EMEF', tipo_ue='EMEF', logradouro='Rua X', numero='100', bairro='Centro', cep=12345678, distrito='Distrito', sub_prefeitura='Sub', nome_dre='DRE Teste', status='ativo')

@pytest.fixture
def escola_2(dre_teste: Any) -> Any:
    """Executa escola 2."""
    return Escola.objects.create(dre=dre_teste, codigo_eol='789012', nome_oficial='Escola 2', nome_nao_oficial='Escola 2', tipo_unidade_admin='EMEF', tipo_ue='EMEF', logradouro='Rua Y', numero='200', bairro='Centro', cep=12345679, distrito='Distrito', sub_prefeitura='Sub', nome_dre='DRE Teste', status='ativo')
