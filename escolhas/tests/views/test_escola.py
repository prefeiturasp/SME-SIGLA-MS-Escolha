"""Módulo tests/views/test_escola."""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status

from escolhas.models import Dre, Escola, Parametrizacao


@pytest.fixture
def dre_bt() -> Any:
    """Executa dre bt."""
    return Dre.objects.create(
        codigo="108100",
        nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
        sigla="DRE - BT",
    )


@pytest.fixture
def dre_ip() -> Any:
    """Executa dre ip."""
    return Dre.objects.create(
        codigo="108200",
        nome="DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
        sigla="DRE - IP",
    )


@pytest.fixture
def param_ativo_emef() -> Any:
    """Executa param ativo emef."""
    return Parametrizacao.objects.create(tipo_ue="EMEF", usar=True)


def criar_escola(dre: Dre, idx: int = 1) -> Escola:
    """Executa criar escola."""
    return Escola.objects.create(
        dre=dre,
        codigo_eol=f"{400000 + idx}",
        nome_oficial=f"ESCOLA TESTE {idx}",
        nome_nao_oficial=f"ET {idx}",
        tipo_unidade_admin="DIRETORIA REGIONAL DE EDUCACAO",
        tipo_ue="EMEF",
        logradouro="Rua Exemplo",
        numero=str(idx),
        bairro=f"Bairro {idx}",
        cep=8000000 + idx,
        distrito="Distrito X",
        sub_prefeitura="Subprefeitura Y",
        nome_dre=dre.nome,
        email=f"escola{idx}@sme.prefeitura.sp.gov.br",
        telefone1="(11) 0000-0000",
        telefone2=None,
        ano_construcao=None,
        propriedade="PROPRIO",
        capacidade_vagas_matutino=100,
        capacidade_vagas_vespertino=100,
        capacidade_vagas_noturno=0,
        capacidade_vagas_intermediario=0,
        capacidade_vagas_integral=0,
        capacidade_vagas_total=200,
        organizacao_parceira=False,
        quantidade_de_funcionarios=10,
        status="ATIVA",
    )


@pytest.mark.django_db
class TestEscolaViewSet:
    """Define TestEscolaViewSet."""

    def test_list_escolas_vazio(
        self, api_client: Any, param_ativo_emef: Any
    ) -> None:
        """Verifica list escolas vazio."""
        url = reverse("escola-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0
        assert "links" in response.data
        assert "results" in response.data

    def test_list_escolas_com_dados(
        self, api_client: Any, dre_bt: Any, param_ativo_emef: Any
    ) -> None:
        """Verifica list escolas com dados."""
        criar_escola(dre_bt, 1)
        criar_escola(dre_bt, 2)
        url = reverse("escola-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2
        item = response.data["results"][0]
        assert "uuid" in item
        assert "dre" in item
        assert set(item["dre"].keys()) == {"uuid", "codigo", "nome", "sigla"}

    def test_retrieve_escola(
        self, api_client: Any, dre_bt: Any, param_ativo_emef: Any
    ) -> None:
        """Verifica retrieve escola."""
        escola = criar_escola(dre_bt, 3)
        url = reverse("escola-detail", kwargs={"pk": escola.uuid})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["uuid"] == str(escola.uuid)
        assert response.data["codigo_eol"] == escola.codigo_eol
        assert response.data["dre"]["codigo"] == dre_bt.codigo
        assert response.data["dre"]["nome"] == dre_bt.nome
        assert response.data["dre"]["sigla"] == dre_bt.sigla

    def test_search_escolas(
        self, api_client: Any, dre_bt: Any, param_ativo_emef: Any
    ) -> None:
        """Verifica search escolas."""
        criar_escola(dre_bt, 1)
        e2 = criar_escola(dre_bt, 2)
        e2.bairro = "VILA SONIA"
        e2.save(update_fields=["bairro"])
        url = reverse("escola-list")
        response = api_client.get(url, {"search": "VILA SONIA"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["bairro"] == "VILA SONIA"
        response = api_client.get(url, {"search": "ESCOLA TESTE 1"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        response = api_client.get(url, {"search": e2.codigo_eol})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_list_escolas_sem_parametrizacao_ativa_retorna_vazio(
        self, api_client: Any, dre_bt: Any
    ) -> None:
        """Verifica list escolas sem parametrizacao ativa retorna vazio."""
        criar_escola(dre_bt, 1)
        criar_escola(dre_bt, 2)
        Parametrizacao.objects.create(tipo_ue="EMEF", usar=False)
        url = reverse("escola-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0

    def test_list_escolas_filtra_por_nome_param(
        self, api_client: Any, dre_bt: Any, param_ativo_emef: Any
    ) -> None:
        """Verifica list escolas filtra por nome param."""
        criar_escola(dre_bt, 1)
        criar_escola(dre_bt, 2)
        url = reverse("escola-list")
        response = api_client.get(url, {"nome": "ESCOLA TESTE 1"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["nome_oficial"] == "ESCOLA TESTE 1"
