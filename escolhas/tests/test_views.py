import pytest
import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from escolhas.models import Escolha


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
def fake_uuid():
    """
    Fixture para gerar UUIDs falsos para testes.
    """
    return uuid.uuid4()


@pytest.mark.django_db
class TestEscolhaViewSet:
    """
    Testes para EscolhaViewSet.
    """

    def test_list_escolhas_sem_autenticacao(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa listagem de escolhas sem autenticação (deve permitir devido a AllowAny).
        """
        url = reverse('escolha-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        
        # Verifica estrutura da resposta paginada
        assert 'links' in response.data
        assert 'count' in response.data
        assert 'page' in response.data
        assert 'page_size' in response.data
        assert 'results' in response.data

    def test_list_escolhas_com_autenticacao(self, authenticated_client, escolha_matematica, escolha_portugues):
        """
        Testa listagem de escolhas com autenticação.
        """
        url = reverse('escolha-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2

    def test_list_escolhas_formato_select(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa listagem de escolhas no formato select (sem paginação).
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'formato': 'select'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Verifica formato select (value/label)
        escolha = response.data[0]
        assert 'value' in escolha
        assert 'label' in escolha
        assert escolha['value'] == str(escolha_matematica.uuid)
        assert escolha['label'] == escolha_matematica.nome

    def test_list_escolhas_ordenacao(self, api_client, escolha_historia, escolha_matematica, escolha_portugues):
        """
        Testa ordenação das escolhas por criado_em (mais recente primeiro).
        """
        url = reverse('escolha-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        
        # Verifica se está ordenado por criado_em descendente
        for i in range(len(results) - 1):
            current_uuid = results[i]['uuid']
            next_uuid = results[i + 1]['uuid']
            
            current_escolha = Escolha.objects.get(uuid=current_uuid)
            next_escolha = Escolha.objects.get(uuid=next_uuid)
            
            assert current_escolha.criado_em >= next_escolha.criado_em

    def test_search_escolhas(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa busca por nome nas escolhas.
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'search': 'Matemática'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['nome'] == 'Professor de Matemática'

    def test_pagination_escolhas(self, api_client, multiple_escolhas):
        """
        Testa paginação das escolhas.
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'page_size': 5})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 5
        assert response.data['page_size'] == 5

    def test_retrieve_escolha_sem_autenticacao(self, api_client, escolha_matematica):
        """
        Testa recuperação de uma escolha específica sem autenticação.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['uuid'] == str(escolha_matematica.uuid)
        assert response.data['nome'] == escolha_matematica.nome
        assert 'criado_em' in response.data
        assert 'atualizado_em' in response.data

    def test_retrieve_escolha_inexistente(self, api_client, fake_uuid):
        """
        Testa recuperação de uma escolha que não existe.
        """
        url = reverse('escolha-detail', kwargs={'pk': fake_uuid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_escolha_sem_autenticacao(self, api_client, escolha_data):
        """
        Testa criação de escolha sem autenticação (deve permitir devido a AllowAny).
        """
        url = reverse('escolha-list')
        response = api_client.post(url, escolha_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == escolha_data['nome']
        assert 'uuid' in response.data
        assert 'criado_em' in response.data
        assert 'atualizado_em' in response.data
        
        # Verifica se foi salvo no banco
        assert Escolha.objects.filter(nome=escolha_data['nome']).exists()

    def test_create_escolha_com_autenticacao(self, authenticated_client, escolha_data):
        """
        Testa criação de escolha com autenticação.
        """
        url = reverse('escolha-list')
        response = authenticated_client.post(url, escolha_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['nome'] == escolha_data['nome']
        assert 'uuid' in response.data
        assert 'criado_em' in response.data
        assert 'atualizado_em' in response.data
        
        # Verifica se foi salvo no banco
        assert Escolha.objects.filter(nome=escolha_data['nome']).exists()

    def test_create_escolha_dados_invalidos(self, authenticated_client, escolha_data_invalid):
        """
        Testa criação de escolha com dados inválidos.
        """
        url = reverse('escolha-list')
        response = authenticated_client.post(url, escolha_data_invalid)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data

    def test_create_escolha_nome_muito_longo(self, authenticated_client, escolha_data_long_name):
        """
        Testa criação de escolha com nome muito longo.
        """
        url = reverse('escolha-list')
        response = authenticated_client.post(url, escolha_data_long_name)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data

    def test_update_escolha_sem_autenticacao(self, api_client, escolha_matematica, escolha_data):
        """
        Testa atualização de escolha sem autenticação (deve permitir devido a AllowAny).
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.put(url, escolha_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == escolha_data['nome']
        assert response.data['uuid'] == str(escolha_matematica.uuid)
        
        # Verifica se foi atualizado no banco
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.nome == escolha_data['nome']

    def test_update_escolha_com_autenticacao(self, authenticated_client, escolha_matematica, escolha_data):
        """
        Testa atualização completa de escolha com autenticação.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = authenticated_client.put(url, escolha_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == escolha_data['nome']
        assert response.data['uuid'] == str(escolha_matematica.uuid)
        
        # Verifica se foi atualizado no banco
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.nome == escolha_data['nome']

    def test_partial_update_escolha(self, authenticated_client, escolha_matematica):
        """
        Testa atualização parcial de escolha.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        data = {'nome': 'Professor de Matemática Avançada'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == data['nome']
        
        # Verifica se foi atualizado no banco
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.nome == data['nome']

    def test_update_escolha_inexistente(self, authenticated_client, fake_uuid, escolha_data):
        """
        Testa atualização de uma escolha que não existe.
        """
        url = reverse('escolha-detail', kwargs={'pk': fake_uuid})
        response = authenticated_client.put(url, escolha_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_escolha_sem_autenticacao(self, api_client, escolha_matematica):
        """
        Testa deleção de escolha sem autenticação (deve permitir devido a AllowAny).
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verifica se foi deletado do banco
        assert not Escolha.objects.filter(uuid=escolha_matematica.uuid).exists()

    def test_delete_escolha_com_autenticacao(self, authenticated_client, escolha_matematica):
        """
        Testa deleção de escolha com autenticação.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verifica se foi deletado do banco
        assert not Escolha.objects.filter(uuid=escolha_matematica.uuid).exists()

    def test_delete_escolha_inexistente(self, authenticated_client, fake_uuid):
        """
        Testa deleção de uma escolha que não existe.
        """
        url = reverse('escolha-detail', kwargs={'pk': fake_uuid})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filtros_backends_configurados(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa se os filtros backends estão configurados corretamente.
        """
        url = reverse('escolha-list')
        
        # Testa DjangoFilterBackend (se houver campos configurados)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Testa SearchFilter
        response = api_client.get(url, {'search': 'Matemática'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        
        # Testa OrderingFilter
        response = api_client.get(url, {'ordering': 'nome'})
        assert response.status_code == status.HTTP_200_OK

    def test_serializer_class_por_action(self, api_client, escolha_matematica):
        """
        Testa se o serializer correto é usado para cada action.
        """
        # List com formato select
        url = reverse('escolha-list')
        response = api_client.get(url, {'formato': 'select'})
        assert response.status_code == status.HTTP_200_OK
        escolha = response.data[0]
        assert 'value' in escolha
        assert 'label' in escolha
        
        # List com formato normal
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        escolha = response.data['results'][0]
        assert 'uuid' in escolha
        assert 'nome' in escolha
        assert len(escolha.keys()) == 2  # EscolhaListSerializer tem apenas uuid e nome
        
        # Retrieve (detail)
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'uuid' in response.data
        assert 'nome' in response.data
        assert 'criado_em' in response.data
        assert 'atualizado_em' in response.data

    def test_custom_pagination_response_format(self, api_client, multiple_escolhas):
        """
        Testa se o formato de resposta da paginação customizada está correto.
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'page_size': 5})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica estrutura da CustomPagination
        assert 'links' in response.data
        assert 'next' in response.data['links']
        assert 'previous' in response.data['links']
        assert 'count' in response.data
        assert 'page' in response.data
        assert 'page_size' in response.data
        assert 'results' in response.data
        
        assert response.data['count'] == 25
        assert response.data['page'] == 1
        assert response.data['page_size'] == 5
        assert len(response.data['results']) == 5

    def test_permissions_allowany(self, api_client, authenticated_client, escolha_matematica, escolha_data):
        """
        Testa se as permissions AllowAny estão funcionando corretamente.
        """
        url_list = reverse('escolha-list')
        url_detail = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        
        # Todas as operações sem autenticação devem funcionar devido a AllowAny
        response = api_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(url_detail)
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.post(url_list, escolha_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        response = api_client.put(url_detail, escolha_data)
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.patch(url_detail, {'nome': 'Novo Nome'})
        assert response.status_code == status.HTTP_200_OK
        
        # Criamos uma nova escolha para testar delete pois a anterior pode ter sido modificada
        nova_escolha = Escolha.objects.create(nome='Teste Delete')
        url_delete = reverse('escolha-detail', kwargs={'pk': nova_escolha.uuid})
        response = api_client.delete(url_delete)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Operações com autenticação também devem funcionar
        response = authenticated_client.post(url_list, {'nome': 'Teste Autenticado'})
        assert response.status_code == status.HTTP_201_CREATED
