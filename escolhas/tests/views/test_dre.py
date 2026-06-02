import pytest
from django.urls import reverse
from rest_framework import status

from escolhas.models import Dre


@pytest.fixture
def dres_criadas():
    return [
        Dre.objects.create(
            codigo="108100",
            nome="DIRETORIA REGIONAL DE EDUCACAO BUTANTA",
            sigla="DRE - BT",
        ),
        Dre.objects.create(
            codigo="108200",
            nome="DIRETORIA REGIONAL DE EDUCACAO IPIRANGA",
            sigla="DRE - IP",
        ),
        Dre.objects.create(
            codigo="108300",
            nome="DIRETORIA REGIONAL DE EDUCACAO PENHA",
            sigla="DRE - PE",
        ),
    ]


@pytest.mark.django_db
class TestDreViewSet:
    def test_list_vazio(self, api_client):
        url = reverse("dre-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0
        assert "links" in response.data
        assert "results" in response.data

    def test_list_com_dados(self, api_client, dres_criadas):
        url = reverse("dre-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

        item = response.data["results"][0]
        assert {"uuid", "codigo", "nome", "sigla"} <= set(item.keys())

    def test_retrieve(self, api_client, dres_criadas):
        dre = dres_criadas[0]
        url = reverse("dre-detail", kwargs={"pk": dre.uuid})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["uuid"] == str(dre.uuid)
        assert response.data["codigo"] == dre.codigo
        assert response.data["nome"] == dre.nome
        assert response.data["sigla"] == dre.sigla

    def test_search(self, api_client, dres_criadas):
        url = reverse("dre-list")
        response = api_client.get(url, {"search": "PENHA"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["sigla"] == "DRE - PE"

    def test_ordering(self, api_client, dres_criadas):
        url = reverse("dre-list")
        response = api_client.get(url, {"ordering": "nome"})
        assert response.status_code == status.HTTP_200_OK
        nomes = [e["nome"] for e in response.data["results"]]
        assert nomes == sorted(nomes)

    def test_pagination(self, api_client):
        for i in range(1, 12):
            Dre.objects.create(
                codigo=f"108{i:02d}00",
                nome=f"DRE {i:02d}",
                sigla=f"DRE - {i:02d}",
            )

        url = reverse("dre-list")
        response = api_client.get(url, {"page_size": 5})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 11
        assert len(response.data["results"]) == 5
        assert response.data["page"] == 1
        assert response.data["page_size"] == 5

        response = api_client.get(url, {"page_size": 5, "page": 2})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5
        assert response.data["page"] == 2
