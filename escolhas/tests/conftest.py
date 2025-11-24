import pytest
from rest_framework.test import APIClient
from escolhas.models import Escolha
import uuid


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
    return Escolha.objects.create(nome='Professor de Matemática')


@pytest.fixture
def escolha_portugues():
    """
    Fixture para criar uma escolha de português.
    """
    return Escolha.objects.create(nome='Professor de Português')


@pytest.fixture
def escolha_historia():
    """
    Fixture para criar uma escolha de história.
    """
    return Escolha.objects.create(nome='Professor de História')


@pytest.fixture
def escolha_ciencias():
    """
    Fixture para criar uma escolha de ciências.
    """
    return Escolha.objects.create(nome='Professor de Ciências')


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
        'nome': 'Nova Escolha de Teste'
    }


@pytest.fixture
def escolha_data_invalid():
    """
    Fixture para dados de escolha inválidos.
    """
    return {
        'nome': ''  # Nome vazio é inválido
    }


@pytest.fixture
def escolha_data_long_name():
    """
    Fixture para dados de escolha com nome muito longo.
    """
    return {
        'nome': 'A' * 201  # Mais que max_length=200
    }


@pytest.fixture
def escolha_data_updated():
    """
    Fixture para dados de escolha atualizados.
    """
    return {
        'nome': 'Escolha Atualizada'
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
    for i in range(25):
        escolha = Escolha.objects.create(nome=f'Escolha Teste {i:02d}')
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def escolhas_ordenadas():
    """
    Fixture para criar escolhas com nomes específicos para teste de ordenação.
    """
    escolhas = []
    nomes = ['Zebra', 'Alpha', 'Beta', 'Gamma']
    for nome in nomes:
        escolha = Escolha.objects.create(nome=nome)
        escolhas.append(escolha)
    return escolhas


@pytest.fixture
def escolhas_para_busca():
    """
    Fixture para criar escolhas específicas para teste de busca.
    """
    escolhas = []
    nomes = [
        'Professor de Matemática',
        'Professor de Física',
        'Coordenador Pedagógico',
        'Diretor de Escola'
    ]
    for nome in nomes:
        escolha = Escolha.objects.create(nome=nome)
        escolhas.append(escolha)
    return escolhas
