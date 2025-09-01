import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from concursos.models import Cargo, Concurso
import uuid


@pytest.fixture
def api_client():
    """
    Fixture para criar um cliente API de teste.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    Fixture para criar um usuário de teste.
    """
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture para criar um cliente API autenticado.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def cargo_analista():
    """
    Fixture para criar um cargo de analista.
    """
    return Cargo.objects.create(nome='Analista de Sistemas')


@pytest.fixture
def cargo_desenvolvedor():
    """
    Fixture para criar um cargo de desenvolvedor.
    """
    return Cargo.objects.create(nome='Desenvolvedor Backend')


@pytest.fixture
def cargo_professor():
    """
    Fixture para criar um cargo de professor.
    """
    return Cargo.objects.create(nome='Professor de Matemática')


@pytest.fixture
def cargos(cargo_analista, cargo_desenvolvedor, cargo_professor):
    """
    Fixture para criar múltiplos cargos de teste.
    """
    return {
        'analista': cargo_analista,
        'desenvolvedor': cargo_desenvolvedor,
        'professor': cargo_professor
    }


@pytest.fixture
def concurso_analista(cargo_analista):
    """
    Fixture para criar um concurso de analista.
    """
    concurso = Concurso.objects.create(nome='Concurso de Analista')
    concurso.cargos.add(cargo_analista)
    return concurso


@pytest.fixture
def concurso_professor(cargo_professor):
    """
    Fixture para criar um concurso de professor.
    """
    concurso = Concurso.objects.create(nome='Concurso de Professor')
    concurso.cargos.add(cargo_professor)
    return concurso


@pytest.fixture
def concursos(concurso_analista, concurso_professor):
    """
    Fixture para criar múltiplos concursos de teste.
    """
    return {
        'analista': concurso_analista,
        'professor': concurso_professor
    }


@pytest.fixture
def cargo_data():
    """
    Fixture para dados de cargo válidos.
    """
    return {
        'nome': 'Novo Cargo de Teste'
    }


@pytest.fixture
def cargo_data_invalid():
    """
    Fixture para dados de cargo inválidos.
    """
    return {
        'nome': ''  # Nome vazio é inválido
    }


@pytest.fixture
def cargo_data_long_name():
    """
    Fixture para dados de cargo com nome muito longo.
    """
    return {
        'nome': 'A' * 201  # Mais que max_length=200
    }


@pytest.fixture
def concurso_data(cargo_analista):
    """
    Fixture para dados de concurso válidos.
    """
    return {
        'nome': 'Novo Concurso de Teste',
        'cargos_ids': [str(cargo_analista.uuid)]
    }


@pytest.fixture
def concurso_data_multiple_cargos(cargo_analista, cargo_desenvolvedor):
    """
    Fixture para dados de concurso com múltiplos cargos.
    """
    return {
        'nome': 'Concurso com Múltiplos Cargos',
        'cargos_ids': [str(cargo_analista.uuid), str(cargo_desenvolvedor.uuid)]
    }


@pytest.fixture
def concurso_data_no_cargos():
    """
    Fixture para dados de concurso sem cargos.
    """
    return {
        'nome': 'Concurso Sem Cargos'
    }


@pytest.fixture
def concurso_data_invalid():
    """
    Fixture para dados de concurso inválidos.
    """
    return {
        'nome': '',  # Nome vazio é inválido
        'cargos_ids': ['invalid-uuid']
    }


@pytest.fixture
def concurso_data_invalid_cargo_ids():
    """
    Fixture para dados de concurso com IDs de cargo inválidos.
    """
    fake_uuid = uuid.uuid4()
    return {
        'nome': 'Concurso com Cargo Inválido',
        'cargos_ids': [str(fake_uuid)]
    }


@pytest.fixture
def fake_uuid():
    """
    Fixture para gerar UUIDs falsos para testes.
    """
    return uuid.uuid4()


@pytest.fixture
def multiple_cargos():
    """
    Fixture para criar múltiplos cargos para testes de paginação.
    """
    cargos = []
    for i in range(25):
        cargo = Cargo.objects.create(nome=f'Cargo Teste {i}')
        cargos.append(cargo)
    return cargos


@pytest.fixture
def multiple_concursos():
    """
    Fixture para criar múltiplos concursos para testes de paginação.
    """
    concursos = []
    for i in range(25):
        concurso = Concurso.objects.create(nome=f'Concurso Teste {i}')
        concursos.append(concurso)
    return concursos 