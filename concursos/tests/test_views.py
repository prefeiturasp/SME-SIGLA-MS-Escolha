import pytest
from django.urls import reverse
from rest_framework import status
from concursos.models import Cargo, Concurso


pytestmark = pytest.mark.django_db


def test_list_cargos_success(authenticated_client, cargos):
    """Testa se a listagem de cargos retorna sucesso."""
    url = reverse('cargo-list')
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    
    # Verificar se os dados estão corretos
    cargos_data = response.data['results']
    cargo_nomes = [cargo['nome'] for cargo in cargos_data]
    assert 'Analista de Sistemas' in cargo_nomes
    assert 'Desenvolvedor Backend' in cargo_nomes
    assert 'Professor de Matemática' in cargo_nomes

def test_list_cargos_with_select_format(authenticated_client, cargos):
    """Testa se a listagem com formato select retorna sem paginação."""
    url = reverse('cargo-list')
    response = authenticated_client.get(url, {'formato': 'select'})
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3  # Sem paginação
    
    # Verificar se os dados estão no formato correto (value/label)
    cargo_data = response.data[0]
    assert 'value' in cargo_data
    assert 'label' in cargo_data
    assert isinstance(cargo_data['value'], str)  # UUID como string
    assert isinstance(cargo_data['label'], str)  # Nome como string


def test_create_cargo_success(authenticated_client, cargo_data):
    """Testa se a criação de cargo funciona corretamente."""
    url = reverse('cargo-list')
    response = authenticated_client.post(url, cargo_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Cargo.objects.count() == 1
    
    # Verificar se o cargo foi criado corretamente
    novo_cargo = Cargo.objects.get(nome='Novo Cargo de Teste')
    assert novo_cargo.uuid is not None
    assert novo_cargo.criado_em is not None
    assert novo_cargo.atualizado_em is not None


def test_retrieve_cargo_success(authenticated_client, cargo_analista):
    """Testa se a recuperação de cargo funciona corretamente."""
    url = reverse('cargo-detail', kwargs={'pk': cargo_analista.uuid})
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'Analista de Sistemas'
    assert response.data['uuid'] == str(cargo_analista.uuid)

def test_retrieve_cargo_not_found(authenticated_client, fake_uuid):
    """Testa se retorna 404 para cargo inexistente."""
    url = reverse('cargo-detail', kwargs={'pk': fake_uuid})
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_cargo_success(authenticated_client, cargo_analista):
    """Testa se a atualização de cargo funciona corretamente."""
    url = reverse('cargo-detail', kwargs={'pk': cargo_analista.uuid})
    data = {'nome': 'Analista de Sistemas Atualizado'}
    response = authenticated_client.put(url, data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'Analista de Sistemas Atualizado'
    
    # Verificar se foi atualizado no banco
    cargo_analista.refresh_from_db()
    assert cargo_analista.nome == 'Analista de Sistemas Atualizado'


def test_delete_cargo_success(authenticated_client, cargo_analista):
    """Testa se a exclusão de cargo funciona corretamente."""
    url = reverse('cargo-detail', kwargs={'pk': cargo_analista.uuid})
    response = authenticated_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Cargo.objects.count() == 0
    
    # Verificar se o cargo foi realmente excluído
    with pytest.raises(Cargo.DoesNotExist):
        Cargo.objects.get(uuid=cargo_analista.uuid)


def test_list_concursos_success(authenticated_client, concursos):
    """Testa se a listagem de concursos retorna sucesso."""
    url = reverse('concurso-list')
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    
    # Verificar se os dados estão corretos
    concursos_data = response.data['results']
    concurso_nomes = [concurso['nome'] for concurso in concursos_data]
    assert 'Concurso de Analista' in concurso_nomes
    assert 'Concurso de Professor' in concurso_nomes

def test_list_concursos_with_select_format(authenticated_client, concursos):
    """Testa se a listagem com formato select retorna sem paginação."""
    url = reverse('concurso-list')
    response = authenticated_client.get(url, {'formato': 'select'})
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2  # Sem paginação
    
    # Verificar se os dados estão no formato correto (value/label)
    concurso_data = response.data[0]
    assert 'value' in concurso_data
    assert 'label' in concurso_data
    assert 'cargos' in concurso_data
    assert isinstance(concurso_data['value'], str)  # UUID como string
    assert isinstance(concurso_data['label'], str)  # Nome como string


def test_create_concurso_success(authenticated_client, concurso_data):
    """Testa se a criação de concurso funciona corretamente."""
    url = reverse('concurso-list')
    response = authenticated_client.post(url, concurso_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Concurso.objects.count() == 1
    
    # Verificar se o concurso foi criado corretamente
    novo_concurso = Concurso.objects.get(nome='Novo Concurso de Teste')
    assert novo_concurso.uuid is not None
    assert novo_concurso.criado_em is not None
    assert novo_concurso.atualizado_em is not None
    
    # Verificar se os cargos foram associados
    assert novo_concurso.cargos.count() == 1

def test_create_concurso_without_nome(authenticated_client):
    """Testa se a criação sem nome retorna erro."""
    url = reverse('concurso-list')
    response = authenticated_client.post(url, {'cargos_ids': []})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in response.data

def test_create_concurso_with_invalid_cargo_ids(authenticated_client, concurso_data_invalid_cargo_ids):
    """Testa se a criação com IDs de cargo inválidos funciona (ignora IDs inválidos)."""
    url = reverse('concurso-list')
    response = authenticated_client.post(url, concurso_data_invalid_cargo_ids)
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verificar se o concurso foi criado sem cargos
    novo_concurso = Concurso.objects.get(nome='Concurso com Cargo Inválido')
    assert novo_concurso.cargos.count() == 0

def test_create_concurso_without_cargos(authenticated_client, concurso_data_no_cargos):
    """Testa se é possível criar um concurso sem cargos."""
    url = reverse('concurso-list')
    response = authenticated_client.post(url, concurso_data_no_cargos)
    
    assert response.status_code == status.HTTP_201_CREATED
    
    novo_concurso = Concurso.objects.get(nome='Concurso Sem Cargos')
    assert novo_concurso.cargos.count() == 0

def test_create_concurso_with_multiple_cargos(authenticated_client, concurso_data_multiple_cargos):
    """Testa se é possível criar um concurso com múltiplos cargos."""
    url = reverse('concurso-list')
    response = authenticated_client.post(url, concurso_data_multiple_cargos)
    
    assert response.status_code == status.HTTP_201_CREATED
    
    novo_concurso = Concurso.objects.get(nome='Concurso com Múltiplos Cargos')
    assert novo_concurso.cargos.count() == 2

def test_retrieve_concurso_success(authenticated_client, concurso_analista):
    """Testa se a recuperação de concurso funciona corretamente."""
    url = reverse('concurso-detail', kwargs={'pk': concurso_analista.uuid})
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'Concurso de Analista'
    assert response.data['uuid'] == str(concurso_analista.uuid)
    assert len(response.data['cargos']) == 1
    assert response.data['cargos'][0]['nome'] == 'Analista de Sistemas'

def test_retrieve_concurso_not_found(authenticated_client, fake_uuid):
    """Testa se retorna 404 para concurso inexistente."""
    url = reverse('concurso-detail', kwargs={'pk': fake_uuid})
    response = authenticated_client.get(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_concurso_success(authenticated_client, concurso_analista, cargo_desenvolvedor):
    """Testa se a atualização de concurso funciona corretamente."""
    url = reverse('concurso-detail', kwargs={'pk': concurso_analista.uuid})
    data = {
        'nome': 'Concurso de Analista Atualizado',
        'cargos_ids': [str(cargo_desenvolvedor.uuid)]
    }
    response = authenticated_client.put(url, data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'Concurso de Analista Atualizado'
    
    # Verificar se foi atualizado no banco
    concurso_analista.refresh_from_db()
    assert concurso_analista.nome == 'Concurso de Analista Atualizado'
    assert concurso_analista.cargos.count() == 1
    assert cargo_desenvolvedor in concurso_analista.cargos.all()


def test_delete_concurso_success(authenticated_client, concurso_analista):
    """Testa se a exclusão de concurso funciona corretamente."""
    url = reverse('concurso-detail', kwargs={'pk': concurso_analista.uuid})
    response = authenticated_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Concurso.objects.count() == 0
    
    # Verificar se o concurso foi realmente excluído
    with pytest.raises(Concurso.DoesNotExist):
        Concurso.objects.get(uuid=concurso_analista.uuid)
