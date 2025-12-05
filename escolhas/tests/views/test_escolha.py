import pytest
import uuid
from django.urls import reverse
from rest_framework import status

from escolhas.models import Escolha


@pytest.mark.django_db
class TestEscolhaViewSet:
    """
    Testes para EscolhaViewSet considerando os novos campos e a action de busca.
    """

    def test_list_escolhas_vazio(self, api_client):
        url = reverse('escolha-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []

    def test_list_escolhas_com_dados(self, api_client, escolha_matematica, escolha_portugues):
        url = reverse('escolha-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        candidatos = {item['candidato_uuid'] for item in response.data['results']}
        assert str(escolha_matematica.candidato_uuid) in candidatos
        assert str(escolha_portugues.candidato_uuid) in candidatos

    def test_filter_candidato_uuid(self, api_client):
        selecionada = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=Escolha.SituacaoChoices.ESCOLHA,
            tipo_vaga=Escolha.TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=Escolha.SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=Escolha.TipoVagaChoices.PRECARIA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )

        url = reverse('escolha-list')
        response = api_client.get(url, {'candidato_uuid': str(selecionada.candidato_uuid)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        resultado = response.data['results'][0]
        assert resultado['candidato_uuid'] == str(selecionada.candidato_uuid)

    def test_create_escolha(self, api_client, escolha_data):
        url = reverse('escolha-list')
        response = api_client.post(url, escolha_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['candidato_uuid'] == escolha_data['candidato_uuid']
        assert Escolha.objects.filter(candidato_uuid=escolha_data['candidato_uuid']).exists()

    def test_create_escolha_dados_invalidos(self, api_client, escolha_data_invalid):
        url = reverse('escolha-list')
        response = api_client.post(url, escolha_data_invalid)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'candidato_uuid' in response.data
        assert 'situacao' in response.data
        assert 'tipo_vaga' in response.data
        assert 'vaga_escola_uuid' in response.data

    def test_update_escolha(self, api_client, escolha_matematica, escolha_data_updated):
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.put(url, escolha_data_updated)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['situacao'] == escolha_data_updated['situacao']
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.situacao == escolha_data_updated['situacao']
        assert escolha_atualizada.tipo_vaga == escolha_data_updated['tipo_vaga']
        assert escolha_atualizada.e_retardatario == escolha_data_updated['e_retardatario']

    def test_partial_update_escolha(self, api_client, escolha_matematica):
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        payload = {'e_retardatario': True}
        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['e_retardatario'] is True
        escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
        assert escolha_atualizada.e_retardatario is True

    def test_delete_escolha(self, api_client, escolha_matematica):
        url = reverse('escolha-detail', kwargs={'pk': escolha_matematica.uuid})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Escolha.objects.filter(uuid=escolha_matematica.uuid).exists()

    def test_busca_por_candidatos(self, api_client):
        escolha_1 = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=Escolha.SituacaoChoices.ESCOLHA,
            tipo_vaga=Escolha.TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )
        escolha_2 = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=Escolha.SituacaoChoices.RECONVOCACAO,
            tipo_vaga=Escolha.TipoVagaChoices.PRECARIA,
            e_retardatario=True,
            vaga_escola_uuid=uuid.uuid4(),
        )
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=Escolha.SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=Escolha.TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )

        url = reverse('escolha-busca')
        payload = {
            'candidato_uuid': [
                str(escolha_1.candidato_uuid),
                str(escolha_2.candidato_uuid),
            ]
        }
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        retornados = {item['candidato_uuid'] for item in response.data['results']}
        assert str(escolha_1.candidato_uuid) in retornados
        assert str(escolha_2.candidato_uuid) in retornados

    def test_busca_payload_invalido(self, api_client):
        url = reverse('escolha-busca')
        response = api_client.post(url, {'candidato_uuid': 'nao-e-lista'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'candidato_uuid' not in response.data
        assert response.data['detail']
