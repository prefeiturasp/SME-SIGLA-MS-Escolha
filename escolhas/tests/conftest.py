"""Módulo tests/conftest."""
from __future__ import annotations
from typing import Any
import uuid
import pytest
from rest_framework.test import APIClient
from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import Dre, Escola, Escolha, VagasEscolas, VagasEscolasLote

@pytest.fixture
def dre() -> Any:
    """Fixture para criar uma DRE."""
    return Dre.objects.create(codigo='01', nome='DRE 01', sigla='DRE-01')

@pytest.fixture
def escola(dre: Any) -> Any:
    """Fixture para criar uma escola."""
    return Escola.objects.create(codigo_eol='000001', nome_oficial='Escola Teste', dre=dre, cep='04001-000')

@pytest.fixture
def lote() -> Any:
    """Fixture para criar um lote de vagas."""
    return VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome='Processo Teste')

@pytest.fixture
def vaga_escola(escola: Any, lote: Any) -> Any:
    """Fixture para criar uma vaga de escola."""
    return VagasEscolas.objects.create(escola=escola, lote=lote, data_fechamento_modulo='2025-01-01', cargo_codigo=100, cargo_descricao='Cargo Teste', vagas_precarias=3, vagas_precarias_restantes=3, vagas_definitivas=5, vagas_definitivas_restantes=5, status='1')

def _criar_escolha(**override: Any) -> Any:
    """Executa  criar escolha."""
    if 'vaga_escola_uuid' in override:
        vaga_uuid = override.pop('vaga_escola_uuid')
        if vaga_uuid:
            try:
                override['vaga_escola'] = VagasEscolas.objects.get(uuid=vaga_uuid)
            except VagasEscolas.DoesNotExist:
                dre = Dre.objects.create(codigo='99', nome='DRE Teste', sigla='DRE-TESTE')
                escola = Escola.objects.create(codigo_eol='999999', nome_oficial='Escola Teste', dre=dre, cep='00000-000')
                lote = VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome='Processo Teste')
                override['vaga_escola'] = VagasEscolas.objects.create(escola=escola, lote=lote, data_fechamento_modulo='2025-01-01', cargo_codigo=100, cargo_descricao='Cargo Teste', vagas_precarias=3, vagas_precarias_restantes=3, vagas_definitivas=5, vagas_definitivas_restantes=5, status='1')
    if 'vaga_escola' not in override:
        dre = Dre.objects.create(codigo='99', nome='DRE Teste', sigla='DRE-TESTE')
        escola = Escola.objects.create(codigo_eol='999999', nome_oficial='Escola Teste', dre=dre, cep='00000-000')
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome='Processo Teste')
        override['vaga_escola'] = VagasEscolas.objects.create(escola=escola, lote=lote, data_fechamento_modulo='2025-01-01', cargo_codigo=100, cargo_descricao='Cargo Teste', vagas_precarias=3, vagas_precarias_restantes=3, vagas_definitivas=5, vagas_definitivas_restantes=5, status='1')
    dados = {'candidato_uuid': uuid.uuid4(), 'concurso_uuid': uuid.uuid4(), 'situacao': SituacaoChoices.ESCOLHA, 'tipo_vaga': TipoVagaChoices.DEFINITIVA, 'e_retardatario': False}
    dados.update(override)
    return Escolha.objects.create(**dados)

@pytest.fixture
def api_client() -> Any:
    """
    Fixture para criar um cliente API de teste.
    """
    return APIClient()

@pytest.fixture
def escolha_matematica() -> Any:
    """
    Fixture para criar uma escolha de matemática.
    """
    return _criar_escolha()

@pytest.fixture
def escolha_portugues() -> Any:
    """
    Fixture para criar uma escolha de português.
    """
    return _criar_escolha()

@pytest.fixture
def escolha_historia() -> Any:
    """
    Fixture para criar uma escolha de história.
    """
    return _criar_escolha()

@pytest.fixture
def escolha_ciencias() -> Any:
    """
    Fixture para criar uma escolha de ciências.
    """
    return _criar_escolha()

@pytest.fixture
def escolhas_multiplas(escolha_matematica: Any, escolha_portugues: Any, escolha_historia: Any, escolha_ciencias: Any) -> Any:
    """
    Fixture para criar múltiplas escolhas de teste.
    """
    return {'matematica': escolha_matematica, 'portugues': escolha_portugues, 'historia': escolha_historia, 'ciencias': escolha_ciencias}

@pytest.fixture
def escolha_data(vaga_escola: Any) -> Any:
    """
    Fixture para dados de escolha válidos.
    """
    return {'candidato_uuid': str(uuid.uuid4()), 'concurso_uuid': str(uuid.uuid4()), 'situacao': SituacaoChoices.ESCOLHA, 'tipo_vaga': TipoVagaChoices.DEFINITIVA, 'e_retardatario': False, 'vaga_escola_uuid': str(vaga_escola.uuid)}

@pytest.fixture
def escolha_data_invalid() -> Any:
    """
    Fixture para dados de escolha inválidos.
    """
    return {'candidato_uuid': None, 'situacao': 'invalida', 'tipo_vaga': 'invalida', 'vaga_escola_uuid': None}

@pytest.fixture
def escolha_data_long_name() -> Any:
    """
    Fixture para dados inválidos com valores fora das choices.
    """
    return {'candidato_uuid': str(uuid.uuid4()), 'situacao': 'muito-longa-para-choice', 'tipo_vaga': 'muito-longa-para-choice', 'e_retardatario': False, 'vaga_escola_uuid': str(uuid.uuid4())}

@pytest.fixture
def escolha_data_updated() -> Any:
    """
    Fixture para dados de escolha atualizados.
    """
    return {'candidato_uuid': str(uuid.uuid4()), 'concurso_uuid': str(uuid.uuid4()), 'situacao': SituacaoChoices.RECONVOCACAO, 'tipo_vaga': TipoVagaChoices.PRECARIA, 'e_retardatario': True}

@pytest.fixture
def fake_uuid() -> Any:
    """
    Fixture para gerar UUIDs falsos para testes.
    """
    return uuid.uuid4()

@pytest.fixture
def multiple_escolhas() -> Any:
    """
    Fixture para criar múltiplas escolhas para testes de paginação.
    """
    escolhas = []
    for _ in range(25):
        escolha = _criar_escolha()
        escolhas.append(escolha)
    return escolhas

@pytest.fixture
def escolhas_ordenadas() -> Any:
    """
    Fixture para criar escolhas com situações específicas para teste de
    ordenação.
    """
    escolhas = []
    situacoes = [SituacaoChoices.ESCOLHA, SituacaoChoices.NAO_ESCOLHA, SituacaoChoices.RECONVOCACAO]
    for situacao in situacoes:
        escolha = _criar_escolha(situacao=situacao)
        escolhas.append(escolha)
    return escolhas

@pytest.fixture
def escolhas_para_busca() -> Any:
    """
    Fixture para criar escolhas específicas para teste de busca.
    """
    escolhas = []
    situacoes = [SituacaoChoices.ESCOLHA, SituacaoChoices.NAO_ESCOLHA, SituacaoChoices.RECONVOCACAO]
    for situacao in situacoes:
        escolha = _criar_escolha(situacao=situacao)
        escolhas.append(escolha)
    return escolhas
