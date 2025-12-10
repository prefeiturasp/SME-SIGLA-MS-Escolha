import pytest
from rest_framework.test import APIClient
from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import Escolha
import uuid


def _criar_escolha(**override):
    dados = {
        'candidato_uuid': uuid.uuid4(),
        'situacao': SituacaoChoices.ESCOLHA,
        'tipo_vaga': TipoVagaChoices.DEFINITIVA,
        'e_retardatario': False,
        'vaga_escola_uuid': uuid.uuid4(),
    }
    dados.update(override)
    return Escolha.objects.create(**dados)


@pytest.fixture
def api_client():
    """
    Fixture para criar um cliente API de teste.
    """
    return APIClient()


@pytest.fixture
def escolha_matematica():
    """
    Fixture para criar uma escolha de matemática.
    """
    return _criar_escolha()


@pytest.fixture
def escolha_portugues():
    """
    Fixture para criar uma escolha de português.
    """
    return _criar_escolha()


@pytest.fixture
def escolha_historia():
    """
    Fixture para criar uma escolha de história.
    """
    return _criar_escolha()


@pytest.fixture
def escolha_ciencias():
    """
    Fixture para criar uma escolha de ciências.
    """
    return _criar_escolha()


@pytest.fixture
def escolhas_multiplas(escolha_matematica, escolha_portugues, escolha_historia, escolha_ciencias):
    """
    Fixture para criar múltiplas escolhas de teste.
    """
    return {
        'matematica': escolha_matematica,
        'portugues': escolha_portugues,
        'historia': escolha_historia,
        'ciencias': escolha_ciencias
    }


@pytest.fixture
def escolha_data():
    """
    Fixture para dados de escolha válidos.
    """
    return {
        'candidato_uuid': str(uuid.uuid4()),
        'situacao': SituacaoChoices.ESCOLHA,
        'tipo_vaga': TipoVagaChoices.DEFINITIVA,
        'e_retardatario': False,
        'vaga_escola_uuid': str(uuid.uuid4()),
    }


@pytest.fixture
def escolha_data_invalid():
    """
    Fixture para dados de escolha inválidos.
    """
    return {
        'candidato_uuid': None,
        'situacao': 'invalida',
        'tipo_vaga': 'invalida',
        'vaga_escola_uuid': None,
    }


@pytest.fixture
def escolha_data_long_name():
    """
    Fixture para dados inválidos com valores fora das choices.
    """
    return {
        'candidato_uuid': str(uuid.uuid4()),
        'situacao': 'muito-longa-para-choice',
        'tipo_vaga': 'muito-longa-para-choice',
        'e_retardatario': False,
        'vaga_escola_uuid': str(uuid.uuid4()),
    }


@pytest.fixture
def escolha_data_updated():
    """
    Fixture para dados de escolha atualizados.
    """
    return {
        'candidato_uuid': str(uuid.uuid4()),
        'situacao': SituacaoChoices.RECONVOCACAO,
        'tipo_vaga': TipoVagaChoices.PRECARIA,
        'e_retardatario': True,
        'vaga_escola_uuid': str(uuid.uuid4()),
    }


@pytest.fixture
def fake_uuid():
    """
    Fixture para gerar UUIDs falsos para testes.
    """
    return uuid.uuid4()


@pytest.fixture
def multiple_escolhas():
    """
    Fixture para criar múltiplas escolhas para testes de paginação.
    """
    escolhas = []
    for _ in range(25):
        escolha = _criar_escolha()
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def escolhas_ordenadas():
    """
    Fixture para criar escolhas com situações específicas para teste de ordenação.
    """
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
    """
    Fixture para criar escolhas específicas para teste de busca.
    """
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
