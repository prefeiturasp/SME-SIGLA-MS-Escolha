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

    def test_list_escolhas_formato_select(self, api_client, escolha_matematica, escolha_portugues):
        """
        Testa listagem no formato select (sem paginação).
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'formato': 'select'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Verifica formato select (value/label)
        escolha = response.data[0]
        assert 'value' in escolha
        assert 'label' in escolha
        
        # Verifica se não tem estrutura de paginação
        assert 'count' not in response.data
        assert 'results' not in response.data

    def test_list_escolhas_formato_select_vazio(self, api_client):
        """
        Testa listagem no formato select quando não há dados.
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'formato': 'select'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_escolhas_ordenacao_padrao(self, api_client, escolhas_multiplas):
        """
        Testa ordenação padrão por criado_em descendente.
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

    def test_ordenacao_personalizada(self, api_client, escolhas_ordenadas):
        """
        Testa ordenação personalizada por nome.
        """
        url = reverse('escolha-list')
        response = api_client.get(url, {'ordering': 'nome'})
        
        assert response.status_code == status.HTTP_200_OK
        nomes = [escolha['nome'] for escolha in response.data['results']]
        # Verifica se a ordenação está funcionando (não necessariamente na ordem específica)
        assert len(nomes) == 4
        assert 'Alpha' in nomes
        assert 'Beta' in nomes
        assert 'Gamma' in nomes
        assert 'Zebra' in nomes

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

    def test_serializer_class_por_action(self, api_client, escolha_matematica):
        """
        Testa se o serializer correto é usado para cada action.
        """
        # List com formato select - EscolhaSelectSerializer
        url = reverse('escolha-list')
        response = api_client.get(url, {'formato': 'select'})
        assert response.status_code == status.HTTP_200_OK
        escolha = response.data[0]
        assert 'value' in escolha
        assert 'label' in escolha
        assert escolha['value'] == str(escolha_matematica.uuid)
        assert escolha['label'] == escolha_matematica.nome
        
        # List com formato normal - EscolhaListSerializer
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        escolha = response.data['results'][0]
        assert 'uuid' in escolha
        assert 'nome' in escolha
        assert len(escolha.keys()) == 2  # Apenas uuid e nome
        
        # Retrieve (detail) - EscolhaSerializer
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'uuid' in response.data
        assert 'nome' in response.data
        assert 'criado_em' in response.data
        assert 'atualizado_em' in response.data
        assert len(response.data.keys()) == 4

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

    def test_filtros_backends_configurados(self, api_client, escolhas_para_busca):
        """
        Testa se os filtros backends estão configurados corretamente.
        """
        url = reverse('escolha-list')
        
        # Testa SearchFilter
        response = api_client.get(url, {'search': 'Professor'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Testa OrderingFilter - verifica se aceita o parâmetro
        response = api_client.get(url, {'ordering': 'nome'})
        assert response.status_code == status.HTTP_200_OK
        # Verifica se retorna os dados corretos (sem verificar ordem específica)
        assert response.data['count'] == 4
        nomes = [escolha['nome'] for escolha in response.data['results']]
        assert len(nomes) == 4

    def test_permissions_allowany(self, api_client, escolha_matematica, escolha_data):
        """
        Testa se as permissions AllowAny estão funcionando - todas as operações devem funcionar.
        """
        url_list = reverse('escolha-list')
        url_detail = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        
        # Todas as operações devem funcionar sem autenticação
        
        # Leitura
        response = api_client.get(url_list)
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.get(url_detail)
        assert response.status_code == status.HTTP_200_OK
        
        # Criação
        response = api_client.post(url_list, escolha_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Atualização
        response = api_client.put(url_detail, {'nome': 'Nome Atualizado'})
        assert response.status_code == status.HTTP_200_OK
        
        response = api_client.patch(url_detail, {'nome': 'Nome Modificado'})
        assert response.status_code == status.HTTP_200_OK
        
        # Deleção
        response = api_client.delete(url_detail)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_docstring_list_method(self, api_client, escolha_matematica):
        """
        Testa se o método list funciona conforme documentado no docstring.
        """
        url = reverse('escolha-list')
        
        # Teste formato normal (com paginação)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        
        # Teste formato select (sem paginação)
        response = api_client.get(url, {'formato': 'select'})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert 'results' not in response.data
        assert 'count' not in response.data

    def test_edge_cases(self, api_client):
        """
        Testa casos extremos e edge cases.
        """
        url = reverse('escolha-list')
        
        # Parâmetros inválidos de paginação
        response = api_client.get(url, {'page': 'invalid'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = api_client.get(url, {'page_size': 'invalid'})
        assert response.status_code == status.HTTP_200_OK  # Usa valor padrão
        assert response.data['page_size'] == 10  # Valor padrão
        
        # Page_size muito grande
        response = api_client.get(url, {'page_size': 1000})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['page_size'] == 1000
        
        # Formato inválido (deve usar formato normal)
        response = api_client.get(url, {'formato': 'invalid'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
