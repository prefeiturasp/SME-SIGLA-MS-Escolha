"""Testes da action busca-por-convocacao."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from escolhas.api.views.escolha import EscolhaViewSet

REPO = (
    "escolhas.api.views.escolha."
    "EscolhaRepository.agregar_por_processo_e_situacao"
)


def _post(payload: dict):
    factory = APIRequestFactory()
    request = factory.post(
        reverse("escolha-busca-por-convocacao"),
        payload,
        format="json",
    )
    view = EscolhaViewSet.as_view({"post": "busca_por_convocacao"})
    return view(request)


def test_busca_por_convocacao_sem_lista_retorna_400():
    """Body sem processo_uuids retorna 400."""
    resposta = _post({})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "processo_uuids" in resposta.data["detail"]

    resposta = _post({"processo_uuids": "nao-lista"})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST


def test_busca_por_convocacao_lista_vazia_retorna_400():
    """Lista vazia de processo_uuids retorna 400."""
    resposta = _post({"processo_uuids": []})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST


@patch(REPO)
def test_busca_por_convocacao_sucesso(mock_agregar):
    """Retorna o resultado agregado pelo repository."""
    pid = str(uuid.uuid4())
    esperado = {
        pid: {
            "escolha": {"total": 1, "candidatos_uuids": ["a"]},
            "nao-escolha": {"total": 0, "candidatos_uuids": []},
            "reconvocacao": {"total": 0, "candidatos_uuids": []},
        }
    }
    mock_agregar.return_value = esperado

    resposta = _post({"processo_uuids": [pid]})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.data == esperado
    mock_agregar.assert_called_once_with([pid])
