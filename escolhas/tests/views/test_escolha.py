import pytest
import uuid
from django.urls import reverse
from rest_framework import status

from escolhas.models import Escolha


@pytest.mark.django_db
class TestEscolhaViewSet:
    """
    Testes para EscolhaViewSet.
    Como a view usa AllowAny, todos os testes são feitos sem autenticação.
    """

    def test_list_escolhas_vazio(self, api_client):
        """
        Testa listagem quando não há escolhas.
        """
        url = reverse('escolha-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
        
        # Verifica estrutura da resposta paginada
        assert 'links' in response.data
        assert 'count' in response.data
        assert 'page' in response.data
        assert 'page_size' in response.data
        assert 'results' in response.data

    def test_list_escolhas_com_dados(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa listagem quando há escolhas cadastradas.
        """
        url = reverse('escolha-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        
        # Verifica se retorna dados corretos
        escolhas_nomes = [escolha['nome'] for escolha in response.data['results']]
        assert 'Professor de Matemática' in escolhas_nomes
        assert 'Professor de Português' in escolhas_nomes

    def test_search_escolhas(self, api_client, escolhas_para_busca):
        """
        Testa busca por nome nas escolhas.
        """
        url = reverse('escolha-list')
        
        # Busca por "Professor"
        response = api_client.get(url, {'search': 'Professor'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Matemática e Física
        
        # Busca por "Matemática"
        response = api_client.get(url, {'search': 'Matemática'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['nome'] == 'Professor de Matemática'
        
        # Busca que não encontra nada
        response = api_client.get(url, {'search': 'Inexistente'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_pagination_escolhas(self, api_client, multiple_escolhas):
        """
        Testa paginação das escolhas.
        """
        url = reverse('escolha-list')
        
        # Primeira página com 5 itens
        response = api_client.get(url, {'page_size': 5})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 5
        assert response.data['page_size'] == 5
        assert response.data['page'] == 1
        
        # Segunda página
        response = api_client.get(url, {'page_size': 5, 'page': 2})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert response.data['page'] == 2

    def test_retrieve_escolha(self, api_client, escolha_matematica):
        """
        Testa recuperação de uma escolha específica.
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

    def test_create_escolha(self, api_client, escolha_data):
        """
        Testa criação de escolha.
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

    def test_create_escolha_dados_invalidos(self, api_client, escolha_data_invalid):
        """
        Testa criação de escolha com dados inválidos.
        """
        url = reverse('escolha-list')
        response = api_client.post(url, escolha_data_invalid)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data

    def test_create_escolha_nome_muito_longo(self, api_client, escolha_data_long_name):
        """
        Testa criação de escolha com nome muito longo.
        """
        url = reverse('escolha-list')
        response = api_client.post(url, escolha_data_long_name)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data

    def test_create_escolha_nome_duplicado(self, api_client, escolha_matematica):
        """
        Testa criação de escolha com nome duplicado (deve permitir).
        """
        url = reverse('escolha-list')
        data = {'nome': escolha_matematica.nome}
        response = api_client.post(url, data)
        
        # O modelo não tem unique constraint, então deve permitir
        assert response.status_code == status.HTTP_201_CREATED
        assert Escolha.objects.filter(nome=escolha_matematica.nome).count() == 2

    def test_update_escolha_completa(self, api_client, escolha_matematica, escolha_data_updated):
        """
        Testa atualização completa de escolha (PUT).
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.put(url, escolha_data_updated)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == escolha_data_updated['nome']
        assert response.data['uuid'] == str(escolha_matematica.uuid)
        
        # Verifica se foi atualizado no banco
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.nome == escolha_data_updated['nome']

    def test_update_escolha_parcial(self, api_client, escolha_matematica):
        """
        Testa atualização parcial de escolha (PATCH).
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        data = {'nome': 'Professor de Matemática Avançada'}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nome'] == data['nome']
        
        # Verifica se foi atualizado no banco
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.nome == data['nome']

    def test_update_escolha_dados_invalidos(self, api_client, escolha_matematica, escolha_data_invalid):
        """
        Testa atualização com dados inválidos.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.put(url, escolha_data_invalid)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in response.data

    def test_update_escolha_inexistente(self, api_client, fake_uuid, escolha_data):
        """
        Testa atualização de uma escolha que não existe.
        """
        url = reverse('escolha-detail', kwargs={'pk': fake_uuid})
        response = api_client.put(url, escolha_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_escolha(self, api_client, escolha_matematica):
        """
        Testa deleção de escolha.
        """
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verifica se foi deletado do banco
        assert not Escolha.objects.filter(uuid=escolha_matematica.uuid).exists()

    def test_delete_escolha_inexistente(self, api_client, fake_uuid):
        """
        Testa deleção de uma escolha que não existe.
        """
        url = reverse('escolha-detail', kwargs={'pk': fake_uuid})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
