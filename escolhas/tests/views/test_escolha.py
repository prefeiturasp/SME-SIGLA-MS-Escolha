import pytest
import uuid
from django.urls import reverse
from rest_framework import status

from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import Escolha, VagasEscolas, VagasEscolasLote, Escola, Dre


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
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=TipoVagaChoices.PRECARIA,
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
        # Remove campos None e converte para strings vazias para permitir serialização
        payload = {k: v if v is not None else '' for k, v in escolha_data_invalid.items()}
        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'candidato_uuid' in response.data or 'situacao' in response.data or 'tipo_vaga' in response.data or 'vaga_escola_uuid' in response.data

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
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),
        )
        escolha_2 = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.RECONVOCACAO,
            tipo_vaga=TipoVagaChoices.PRECARIA,
            e_retardatario=True,
            vaga_escola_uuid=uuid.uuid4(),
        )
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
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
        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        # O endpoint retorna uma lista diretamente, não um objeto com 'results'
        assert isinstance(response.data, list)
        assert len(response.data) == 2
        retornados = {item['candidato_uuid'] for item in response.data}
        assert str(escolha_1.candidato_uuid) in retornados
        assert str(escolha_2.candidato_uuid) in retornados

    def test_busca_payload_invalido(self, api_client):
        url = reverse('escolha-busca')
        response = api_client.post(url, {'candidato_uuid': 'nao-e-lista'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'candidato_uuid' not in response.data
        assert response.data['detail']

    def test_create_escolha_decrementa_vaga_definitiva(self, api_client):
        """Testa se a criação de uma escolha com vaga definitiva decrementa vagas_definitivas_restantes."""
        # Cria DRE, Escola e VagaEscola
        dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
        escola = Escola.objects.create(
            codigo_eol="000001",
            nome_oficial="Escola Teste",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome="Proc")
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=100,
            cargo_descricao="Cargo Teste",
            vagas_precarias=2,
            vagas_precarias_restantes=2,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )
        
        # Valor inicial
        vaga_escola.refresh_from_db()
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        
        # Cria escolha via POST
        url = reverse('escolha-list')
        payload = {
            'candidato_uuid': str(uuid.uuid4()),
            'concurso_uuid': str(uuid.uuid4()),
            'situacao': SituacaoChoices.ESCOLHA,
            'tipo_vaga': TipoVagaChoices.DEFINITIVA,
            'e_retardatario': False,
            'vaga_escola_uuid': str(vaga_escola.uuid),
        }
        response = api_client.post(url, payload)
        
        # Verifica que a escolha foi criada
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica que a vaga foi decrementada
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial - 1
        # Verifica que vagas precárias não foram alteradas
        assert vaga_escola.vagas_precarias_restantes == 2

    def test_create_escolha_decrementa_vaga_precaria(self, api_client):
        """Testa se a criação de uma escolha com vaga precária decrementa vagas_precarias_restantes."""
        # Cria DRE, Escola e VagaEscola
        dre = Dre.objects.create(codigo="02", nome="DRE 02", sigla="DRE-02")
        escola = Escola.objects.create(
            codigo_eol="000002",
            nome_oficial="Escola Teste 2",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome="Proc")
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=101,
            cargo_descricao="Cargo Teste 2",
            vagas_precarias=3,
            vagas_precarias_restantes=3,
            vagas_definitivas=4,
            vagas_definitivas_restantes=4,
            status="1"
        )
        
        # Valor inicial
        vaga_escola.refresh_from_db()
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
        
        # Cria escolha via POST
        url = reverse('escolha-list')
        payload = {
            'candidato_uuid': str(uuid.uuid4()),
            'concurso_uuid': str(uuid.uuid4()),
            'situacao': SituacaoChoices.ESCOLHA,
            'tipo_vaga': TipoVagaChoices.PRECARIA,
            'e_retardatario': False,
            'vaga_escola_uuid': str(vaga_escola.uuid),
        }
        response = api_client.post(url, payload)
        
        # Verifica que a escolha foi criada
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica que a vaga foi decrementada
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial - 1
        # Verifica que vagas definitivas não foram alteradas
        assert vaga_escola.vagas_definitivas_restantes == 4

    def test_create_escolha_nao_escolha_nao_decrementa(self, api_client):
        """Testa que escolhas com situação diferente de 'escolha' não decrementam vagas."""
        # Cria DRE, Escola e VagaEscola
        dre = Dre.objects.create(codigo="03", nome="DRE 03", sigla="DRE-03")
        escola = Escola.objects.create(
            codigo_eol="000003",
            nome_oficial="Escola Teste 3",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid.uuid4(), processo_nome="Proc")
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=102,
            cargo_descricao="Cargo Teste 3",
            vagas_precarias=2,
            vagas_precarias_restantes=2,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )
        
        # Valor inicial
        vaga_escola.refresh_from_db()
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
        
        # Cria escolha com situação 'nao-escolha'
        url = reverse('escolha-list')
        payload = {
            'candidato_uuid': str(uuid.uuid4()),
            'concurso_uuid': str(uuid.uuid4()),
            'situacao': SituacaoChoices.NAO_ESCOLHA,
            'tipo_vaga': TipoVagaChoices.DEFINITIVA,
            'e_retardatario': False,
            'vaga_escola_uuid': str(vaga_escola.uuid),
        }
        response = api_client.post(url, payload)
        
        # Verifica que a escolha foi criada
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica que as vagas NÃO foram decrementadas
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial
