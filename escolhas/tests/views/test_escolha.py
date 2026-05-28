import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import (
    Dre,
    Escola,
    Escolha,
    VagasEscolas,
    VagasEscolasLote,
)


@pytest.mark.django_db
def test_list_escolhas_vazio(api_client):
    url = reverse("escolha-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_escolhas_com_dados(
    api_client, escolha_matematica, escolha_portugues
):
    url = reverse("escolha-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    candidatos = {item["candidato_uuid"] for item in response.data["results"]}
    assert str(escolha_matematica.candidato_uuid) in candidatos
    assert str(escolha_portugues.candidato_uuid) in candidatos


@pytest.mark.django_db
def test_filter_candidato_uuid(api_client):
    # Criar DRE, Escola e VagaEscola para os testes
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
    vaga_escola_1 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo Teste",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )
    vaga_escola_2 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=101,
        cargo_descricao="Cargo Teste 2",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )

    selecionada = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola_1,
    )
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.PRECARIA,
        e_retardatario=False,
        vaga_escola=vaga_escola_2,
    )

    url = reverse("escolha-list")
    response = api_client.get(
        url, {"candidato_uuid": str(selecionada.candidato_uuid)}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    resultado = response.data["results"][0]
    assert resultado["candidato_uuid"] == str(selecionada.candidato_uuid)


@pytest.mark.django_db
def test_create_escolha(api_client, escolha_data):
    url = reverse("escolha-list")
    response = api_client.post(url, escolha_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["candidato_uuid"] == escolha_data["candidato_uuid"]
    assert Escolha.objects.filter(
        candidato_uuid=escolha_data["candidato_uuid"]
    ).exists()


@pytest.mark.django_db
def test_create_escolha_dados_invalidos(api_client, escolha_data_invalid):
    url = reverse("escolha-list")
    # Remove campos None e converte para strings vazias para permitir serialização  # noqa: E501
    payload = {
        k: v if v is not None else "" for k, v in escolha_data_invalid.items()
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "candidato_uuid" in response.data
        or "situacao" in response.data
        or "tipo_vaga" in response.data
        or "vaga_escola_uuid" in response.data
    )


@pytest.mark.django_db
def test_update_escolha(api_client, escolha_matematica, escolha_data_updated):
    url = reverse("escolha-detail", kwargs={"pk": escolha_matematica.uuid})
    response = api_client.put(url, escolha_data_updated)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["situacao"] == escolha_data_updated["situacao"]
    escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
    assert escolha_atualizada.situacao == escolha_data_updated["situacao"]
    assert escolha_atualizada.tipo_vaga == escolha_data_updated["tipo_vaga"]
    assert (
        escolha_atualizada.e_retardatario
        == escolha_data_updated["e_retardatario"]
    )


@pytest.mark.django_db
def test_partial_update_escolha(api_client, escolha_matematica):
    url = reverse("escolha-detail", kwargs={"pk": escolha_matematica.uuid})
    payload = {"e_retardatario": True}
    response = api_client.patch(url, payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["e_retardatario"] is True
    escolha_atualizada = Escolha.objects.get(uuid=escolha_matematica.uuid)
    assert escolha_atualizada.e_retardatario is True


@pytest.mark.django_db
def test_delete_escolha(api_client, escolha_matematica):
    url = reverse("escolha-detail", kwargs={"pk": escolha_matematica.uuid})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Escolha.objects.filter(uuid=escolha_matematica.uuid).exists()


@pytest.mark.django_db
def test_busca_por_candidatos(api_client):
    # Criar DRE, Escola e VagaEscola para os testes
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
    vaga_escola_1 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo Teste",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )
    vaga_escola_2 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=101,
        cargo_descricao="Cargo Teste 2",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )
    vaga_escola_3 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=102,
        cargo_descricao="Cargo Teste 3",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )

    escolha_1 = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola_1,
    )
    escolha_2 = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.RECONVOCACAO,
        tipo_vaga=TipoVagaChoices.PRECARIA,
        e_retardatario=True,
        vaga_escola=vaga_escola_2,
    )
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola_3,
    )

    url = reverse("escolha-busca")
    payload = {
        "candidato_uuid": [
            str(escolha_1.candidato_uuid),
            str(escolha_2.candidato_uuid),
        ]
    }
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    # O endpoint retorna uma lista diretamente, não um objeto com 'results'
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    retornados = {item["candidato_uuid"] for item in response.data}
    assert str(escolha_1.candidato_uuid) in retornados
    assert str(escolha_2.candidato_uuid) in retornados


@pytest.mark.django_db
def test_busca_payload_invalido(api_client):
    url = reverse("escolha-busca")
    response = api_client.post(url, {"candidato_uuid": "nao-e-lista"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "candidato_uuid" not in response.data
    assert response.data["detail"]


@pytest.mark.django_db
def test_create_escolha_decrementa_vaga_definitiva(api_client):
    """
    Testa se a criação de uma escolha com vaga definitiva decrementa
    vagas_definitivas_restantes.
    """
    # Cria DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
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
        status="1",
    )

    # Valor inicial
    vaga_escola.refresh_from_db()
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

    # Cria escolha via POST
    url = reverse("escolha-list")
    payload = {
        "candidato_uuid": str(uuid.uuid4()),
        "concurso_uuid": str(uuid.uuid4()),
        "situacao": SituacaoChoices.ESCOLHA,
        "tipo_vaga": TipoVagaChoices.DEFINITIVA,
        "e_retardatario": False,
        "vaga_escola_uuid": str(vaga_escola.uuid),
    }
    response = api_client.post(url, payload)

    # Verifica que a escolha foi criada
    assert response.status_code == status.HTTP_201_CREATED

    # Verifica que a vaga foi decrementada
    vaga_escola.refresh_from_db()
    assert (
        vaga_escola.vagas_definitivas_restantes
        == vagas_definitivas_inicial - 1
    )
    # Verifica que vagas precárias não foram alteradas
    assert vaga_escola.vagas_precarias_restantes == 2


@pytest.mark.django_db
def test_create_escolha_decrementa_vaga_precaria(api_client):
    """
    Testa se a criação de uma escolha com vaga precária decrementa
    vagas_precarias_restantes.
    """
    # Cria DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="02", nome="DRE 02", sigla="DRE-02")
    escola = Escola.objects.create(
        codigo_eol="000002",
        nome_oficial="Escola Teste 2",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
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
        status="1",
    )

    # Valor inicial
    vaga_escola.refresh_from_db()
    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

    # Cria escolha via POST
    url = reverse("escolha-list")
    payload = {
        "candidato_uuid": str(uuid.uuid4()),
        "concurso_uuid": str(uuid.uuid4()),
        "situacao": SituacaoChoices.ESCOLHA,
        "tipo_vaga": TipoVagaChoices.PRECARIA,
        "e_retardatario": False,
        "vaga_escola_uuid": str(vaga_escola.uuid),
    }
    response = api_client.post(url, payload)

    # Verifica que a escolha foi criada
    assert response.status_code == status.HTTP_201_CREATED

    # Verifica que a vaga foi decrementada
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial - 1
    # Verifica que vagas definitivas não foram alteradas
    assert vaga_escola.vagas_definitivas_restantes == 4


@pytest.mark.django_db
def test_create_escolha_nao_escolha_nao_decrementa(api_client):
    """
    Testa que escolhas com situação diferente de 'escolha' não decrementam
    vagas.
    """
    # Cria DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="03", nome="DRE 03", sigla="DRE-03")
    escola = Escola.objects.create(
        codigo_eol="000003",
        nome_oficial="Escola Teste 3",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
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
        status="1",
    )

    # Valor inicial
    vaga_escola.refresh_from_db()
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

    # Cria escolha com situação 'nao-escolha'
    url = reverse("escolha-list")
    payload = {
        "candidato_uuid": str(uuid.uuid4()),
        "concurso_uuid": str(uuid.uuid4()),
        "situacao": SituacaoChoices.NAO_ESCOLHA,
        "tipo_vaga": TipoVagaChoices.DEFINITIVA,
        "e_retardatario": False,
        "vaga_escola_uuid": str(vaga_escola.uuid),
    }
    response = api_client.post(url, payload)

    # Verifica que a escolha foi criada
    assert response.status_code == status.HTTP_201_CREATED

    # Verifica que as vagas NÃO foram decrementadas
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial


@pytest.mark.django_db
def test_agrupar_por_cargo_retorna_dict_so_com_situacao_escolha(api_client):
    # Monta DRE/Escola/Lote e duas vagas com cargos distintos
    dre = Dre.objects.create(codigo="10", nome="DRE 10", sigla="DRE-10")
    escola = Escola.objects.create(
        codigo_eol="000010", nome_oficial="Escola 10", dre=dre, cep="04001-000"
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
    vaga_cargo_100 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo 100",
        vagas_precarias=0,
        vagas_precarias_restantes=0,
        vagas_definitivas=10,
        vagas_definitivas_restantes=10,
        status="1",
    )
    vaga_cargo_101 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=101,
        cargo_descricao="Cargo 101",
        vagas_precarias=0,
        vagas_precarias_restantes=0,
        vagas_definitivas=10,
        vagas_definitivas_restantes=10,
        status="1",
    )

    # Cria escolhas: 2 para cargo 100 com situacao ESCOLHA; 1 NAO_ESCOLHA (ignorada)  # noqa: E501
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_cargo_100,
    )
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_cargo_100,
    )
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_cargo_100,
    )
    # 1 escolha válida para cargo 101
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.PRECARIA,
        e_retardatario=False,
        vaga_escola=vaga_cargo_101,
    )

    url = reverse("escolha-agrupar-por-cargo")
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    # Deve retornar um dict { "100": 2, "101": 1 } (apenas situacao=ESCOLHA)
    assert isinstance(resp.data, dict)
    assert resp.data.get("100") == 2
    assert resp.data.get("101") == 1


@pytest.mark.django_db
def test_reconvocacao_endpoint(api_client):
    """Testa endpoint de reconvocação."""
    # Criar DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
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
        status="1",
    )

    # Criar escolhas com diferentes situações
    escolha_reconvocacao = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.RECONVOCACAO,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )

    url = reverse("escolha-reconvocacao")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) == 1
    assert response.data[0]["uuid"] == str(escolha_reconvocacao.uuid)
    assert response.data[0]["candidato_uuid"] == str(
        escolha_reconvocacao.candidato_uuid
    )


@pytest.mark.django_db
def test_importacao_prodam_sucesso(api_client, settings):
    """Testa importação Prodam com sucesso."""
    from unittest.mock import Mock, patch

    # Configurar settings
    settings.CANDIDATOS_API_URL = "http://test-api.com"

    # Criar DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="123456",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
    VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo Teste",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid = uuid.uuid4()

    # Mock do CandidatoAPIService
    mock_candidatos = [
        {
            "uuid": str(candidato_uuid),
            "cpf": "12345678901",
            "nome": "Candidato Teste",
        }
    ]

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "processo_uuid": str(processo_uuid),
        "escolhas": [
            {
                "cpf": "12345678901",
                "codigo_cargo": "100",
                "codigo_eol": "123456",
                "tipo_vaga": "D",
                "situacao": "ESCOLHA",
            }
        ],
    }

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos_por_cpfs.return_value = mock_candidatos
        mock_service_class.return_value = mock_service

        url = reverse("escolha-importacao-prodam")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["escolhas_criadas"] == 1
        assert len(response.data["escolhas"]) == 1
        assert response.data["escolhas"][0]["candidato_uuid"] == str(
            candidato_uuid
        )
        assert (
            response.data["escolhas"][0]["situacao"] == SituacaoChoices.ESCOLHA
        )

        # Verificar que escolha foi criada
        assert Escolha.objects.filter(candidato_uuid=candidato_uuid).exists()


@pytest.mark.django_db
def test_importacao_prodam_candidato_nao_encontrado(api_client, settings):
    """Testa importação Prodam quando candidato não é encontrado."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "processo_uuid": str(processo_uuid),
        "escolhas": [
            {
                "cpf": "12345678901",
                "codigo_cargo": "100",
                "codigo_eol": "123456",
                "tipo_vaga": "D",
                "situacao": "ESCOLHA",
            }
        ],
    }

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos_por_cpfs.return_value = []  # Nenhum candidato encontrado  # noqa: E501
        mock_service_class.return_value = mock_service

        url = reverse("escolha-importacao-prodam")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["escolhas_criadas"] == 0
        assert "erros" in response.data
        assert len(response.data["erros"]) == 1
        assert response.data["erros"][0]["erro"] == "Candidato não encontrado"


@pytest.mark.django_db
def test_importacao_prodam_multiplas_escolhas(api_client, settings):
    """Testa importação Prodam com múltiplas escolhas."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    # Criar DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="123456",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
    VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo Teste",
        vagas_precarias=2,
        vagas_precarias_restantes=2,
        vagas_definitivas=5,
        vagas_definitivas_restantes=5,
        status="1",
    )

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid_1 = uuid.uuid4()
    candidato_uuid_2 = uuid.uuid4()

    mock_candidatos = [
        {
            "uuid": str(candidato_uuid_1),
            "cpf": "12345678901",
            "nome": "Candidato 1",
        },
        {
            "uuid": str(candidato_uuid_2),
            "cpf": "98765432100",
            "nome": "Candidato 2",
        },
    ]

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "processo_uuid": str(processo_uuid),
        "escolhas": [
            {
                "cpf": "12345678901",
                "codigo_cargo": "100",
                "codigo_eol": "123456",
                "tipo_vaga": "D",
                "situacao": "ESCOLHA",
            },
            {
                "cpf": "98765432100",
                "codigo_cargo": "100",
                "codigo_eol": "123456",
                "tipo_vaga": "P",
                "situacao": "NAO-ESCOLHA",
            },
        ],
    }

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos_por_cpfs.return_value = mock_candidatos
        mock_service_class.return_value = mock_service

        url = reverse("escolha-importacao-prodam")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["escolhas_criadas"] == 2
        assert len(response.data["escolhas"]) == 2


@pytest.mark.django_db
def test_importacao_prodam_mapeamento_situacao(api_client, settings):
    """Testa mapeamento de situações na importação Prodam."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid = uuid.uuid4()

    mock_candidatos = [
        {
            "uuid": str(candidato_uuid),
            "cpf": "12345678901",
            "nome": "Candidato Teste",
        }
    ]

    # Testar diferentes situações
    situacoes_teste = [
        ("ESCOLHA", SituacaoChoices.ESCOLHA),
        ("NAO-ESCOLHA", SituacaoChoices.NAO_ESCOLHA),
        ("RECONVOCACAO", SituacaoChoices.RECONVOCACAO),
        ("PENDENTE", SituacaoChoices.NAO_ESCOLHA),  # PENDENTE vira NAO_ESCOLHA
        (
            "INVALIDO",
            SituacaoChoices.NAO_ESCOLHA,
        ),  # Valor inválido vira NAO_ESCOLHA
    ]

    for situacao_input, situacao_esperada in situacoes_teste:
        payload = {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "escolhas": [
                {
                    "cpf": "12345678901",
                    "codigo_cargo": "100",
                    "codigo_eol": "",  # Campo opcional, mas precisa estar presente  # noqa: E501
                    "situacao": situacao_input,
                }
            ],
        }

        with patch(
            "escolhas.views.escolha.CandidatoAPIService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.buscar_candidatos_por_cpfs.return_value = (
                mock_candidatos
            )
            mock_service_class.return_value = mock_service

            url = reverse("escolha-importacao-prodam")
            response = api_client.post(url, payload, format="json")

            assert response.status_code == status.HTTP_201_CREATED
            assert (
                response.data["escolhas"][0]["situacao"] == situacao_esperada
            )

            # Limpar escolhas criadas para próximo teste
            Escolha.objects.filter(candidato_uuid=candidato_uuid).delete()


@pytest.mark.django_db
def test_importacao_prodam_mapeamento_tipo_vaga(api_client, settings):
    """Testa mapeamento de tipo_vaga na importação Prodam."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid = uuid.uuid4()

    mock_candidatos = [
        {
            "uuid": str(candidato_uuid),
            "cpf": "12345678901",
            "nome": "Candidato Teste",
        }
    ]

    # Testar diferentes tipos de vaga
    tipos_teste = [
        ("P", TipoVagaChoices.PRECARIA),
        ("D", TipoVagaChoices.DEFINITIVA),
        ("p", TipoVagaChoices.PRECARIA),  # Minúsculo
        ("d", TipoVagaChoices.DEFINITIVA),  # Minúsculo
        ("X", None),  # Inválido
    ]

    for tipo_input, tipo_esperado in tipos_teste:
        payload = {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "escolhas": [
                {
                    "cpf": "12345678901",
                    "codigo_cargo": "100",
                    "codigo_eol": "",  # Campo opcional, mas precisa estar presente  # noqa: E501
                    "tipo_vaga": tipo_input,
                    "situacao": "ESCOLHA",
                }
            ],
        }

        with patch(
            "escolhas.views.escolha.CandidatoAPIService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.buscar_candidatos_por_cpfs.return_value = (
                mock_candidatos
            )
            mock_service_class.return_value = mock_service

            url = reverse("escolha-importacao-prodam")
            response = api_client.post(url, payload, format="json")

            assert response.status_code == status.HTTP_201_CREATED

            # Verificar tipo_vaga na escolha criada
            escolha = Escolha.objects.filter(
                candidato_uuid=candidato_uuid
            ).first()
            assert escolha.tipo_vaga == tipo_esperado

            # Limpar escolhas criadas para próximo teste
            Escolha.objects.filter(candidato_uuid=candidato_uuid).delete()


@pytest.mark.django_db
def test_importacao_prodam_codigo_eol_normalizado(api_client, settings):
    """Testa normalização de código EOL na importação Prodam."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    # Criar DRE, Escola e VagaEscola
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    escola = Escola.objects.create(
        codigo_eol="123456",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )
    lote = VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(), processo_nome="Proc"
    )
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
        status="1",
    )

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid = uuid.uuid4()

    mock_candidatos = [
        {
            "uuid": str(candidato_uuid),
            "cpf": "12345678901",
            "nome": "Candidato Teste",
        }
    ]

    # Testar com código EOL sem zeros à esquerda
    payload = {
        "concurso_uuid": str(concurso_uuid),
        "processo_uuid": str(processo_uuid),
        "escolhas": [
            {
                "cpf": "12345678901",
                "codigo_cargo": "100",
                "codigo_eol": "123456",  # Já está normalizado
                "tipo_vaga": "D",
                "situacao": "ESCOLHA",
            }
        ],
    }

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos_por_cpfs.return_value = mock_candidatos
        mock_service_class.return_value = mock_service

        url = reverse("escolha-importacao-prodam")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        escolha = Escolha.objects.filter(candidato_uuid=candidato_uuid).first()
        assert escolha.vaga_escola == vaga_escola


@pytest.mark.django_db
def test_importacao_prodam_payload_invalido(api_client):
    """Testa importação Prodam com payload inválido."""
    payload = {"concurso_uuid": "invalid-uuid", "escolhas": []}

    url = reverse("escolha-importacao-prodam")
    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_importacao_prodam_escolha_sem_codigo_eol(api_client, settings):
    """Testa importação Prodam com escolha sem código EOL."""
    from unittest.mock import Mock, patch

    settings.CANDIDATOS_API_URL = "http://test-api.com"

    processo_uuid = uuid.uuid4()
    concurso_uuid = uuid.uuid4()
    candidato_uuid = uuid.uuid4()

    mock_candidatos = [
        {
            "uuid": str(candidato_uuid),
            "cpf": "12345678901",
            "nome": "Candidato Teste",
        }
    ]

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "processo_uuid": str(processo_uuid),
        "escolhas": [
            {
                "cpf": "12345678901",
                "codigo_cargo": "100",
                "codigo_eol": "",  # Campo opcional vazio
                "situacao": "NAO-ESCOLHA",
            }
        ],
    }

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos_por_cpfs.return_value = mock_candidatos
        mock_service_class.return_value = mock_service

        url = reverse("escolha-importacao-prodam")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        escolha = Escolha.objects.filter(candidato_uuid=candidato_uuid).first()
        assert (
            escolha.vaga_escola is None
        )  # Não deve ter vaga_escola quando não há codigo_eol


# --- Testes da action buscar_candidatos e list com historico (feature/143715-consulta-concursado) ---  # noqa: E501


@pytest.mark.django_db
def test_buscar_candidatos_sem_parametros_retorna_400(api_client):
    """
    GET buscar-candidatos sem nome, cpf, rg ou registro_funcional deve retornar
    400.
    """
    url = reverse("escolha-buscar-candidatos")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert (
        "nome" in response.data["detail"] or "cpf" in response.data["detail"]
    )


@pytest.mark.django_db
def test_buscar_candidatos_com_parametro_retorna_200(api_client):
    """
    GET buscar-candidatos com parâmetro deve delegar ao serviço e retornar 200
    com lista.
    """
    from unittest.mock import Mock, patch

    url = reverse("escolha-buscar-candidatos")
    mock_candidatos = [
        {"nome": "João Silva", "cpf": "12345678901", "concursos": []}
    ]

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos.return_value = mock_candidatos
        mock_service_class.return_value = mock_service

        response = api_client.get(url, {"nome": "João"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data == mock_candidatos
        mock_service.buscar_candidatos.assert_called_once_with(
            nome="João", cpf=None, rg=None, registro_funcional=None
        )


@pytest.mark.django_db
def test_buscar_candidatos_servico_retorna_none_retorna_400(api_client):
    """Quando o serviço retorna None (erro), deve retornar 502."""
    from unittest.mock import Mock, patch

    url = reverse("escolha-buscar-candidatos")

    with patch(
        "escolhas.views.escolha.CandidatoAPIService"
    ) as mock_service_class:
        mock_service = Mock()
        mock_service.buscar_candidatos.return_value = None
        mock_service_class.return_value = mock_service

        response = api_client.get(url, {"cpf": "12345678901"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["detail"]
            == "Erro ao consultar serviço de candidatos."
        )


@pytest.mark.django_db
def test_list_escolhas_inclui_campo_historico(api_client, escolha_matematica):
    """Listagem inclui campo historico (lista) em cada item."""
    from escolhas.models import HistoricoEscolha

    HistoricoEscolha.objects.create(
        escolha=escolha_matematica,
        situacao_anterior=None,
        situacao_nova=SituacaoChoices.ESCOLHA,
    )
    url = reverse("escolha-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1
    resultado = next(
        (
            r
            for r in response.data["results"]
            if str(r["candidato_uuid"])
            == str(escolha_matematica.candidato_uuid)
        ),
        None,
    )
    assert resultado is not None
    assert "historico" in resultado
    assert isinstance(resultado["historico"], list)
    assert len(resultado["historico"]) >= 1
    assert (
        resultado["historico"][0]["situacao_nova"] == SituacaoChoices.ESCOLHA
    )
    assert "uuid" in resultado["historico"][0]
    assert "criado_em" in resultado["historico"][0]
