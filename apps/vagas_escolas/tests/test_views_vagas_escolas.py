"""Módulo tests/views/test_vagas_escolas_viewset."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status

from vagas_escolas.models import VagasEscolas
from vagas_escolas.services.exceptions import TipoUEDesabilitadoException

pytestmark = pytest.mark.django_db


def payload(processo_uuid, eol1="123456", eol2=None):
    """Payload."""
    vagas = [
        {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": eol1,
            "vagas_precarias": 2,
            "vagas_definitivas": 3,
            "status": "ativo",
        }
    ]
    if eol2:
        vagas.append(
            {
                "data_fechamento_modulo": "2025-09-15",
                "cargo_codigo": 456,
                "cargo_descricao": "Professor de Português",
                "codigo_eol": eol2,
                "vagas_precarias": 1,
                "vagas_definitivas": 2,
                "status": "ativo",
            }
        )
    return {
        "processo_uuid": str(processo_uuid),
        "processo_nome": "Processo Teste",
        "concurso_uuid": str(uuid4()),
        "vagas": vagas,
    }


def test_post_cria_lote_e_vagas_e_list_retorna_so_ultimo_lote(
    api_client, escola_1, escola_2
):
    """Verifica post cria lote e vagas e list retorna so ultimo lote."""
    p_uuid = uuid4()
    url = reverse("vagas-escolas-list")
    resp1 = api_client.post(
        url, payload(p_uuid, eol1="123456", eol2="789012"), format="json"
    )
    assert resp1.status_code in (201, 207)
    lote1_uuid = resp1.data["lote_uuid"]
    assert VagasEscolas.objects.filter(lote__uuid=lote1_uuid).count() == 2
    resp2 = api_client.post(url, payload(p_uuid, eol1="123456"), format="json")
    assert resp2.status_code in (201, 207)
    lote2_uuid = resp2.data["lote_uuid"]
    assert lote2_uuid != lote1_uuid
    assert VagasEscolas.objects.filter(lote__uuid=lote2_uuid).count() == 1
    list_resp = api_client.get(url, {"processo_uuid": str(p_uuid)})
    assert list_resp.status_code == 200
    vagas = list_resp.data.get("vagas", [])
    assert len(vagas) == 1
    assert vagas[0]["lote_uuid"] == lote2_uuid
    assert list_resp.data["total_vagas"] == 5
    assert isinstance(list_resp.data["dres"], list)
    assert {"codigo", "nome", "uuid"} <= set(list_resp.data["dres"][0].keys())


def test_list_processo_inexistente_retorna_vazio(api_client, escola_1):
    """Verifica list processo inexistente retorna vazio."""
    url = reverse("vagas-escolas-list")
    resp = api_client.get(url, {"processo_uuid": str(uuid4())})
    assert resp.status_code == 200
    assert resp.data.get("vagas") == []
    assert resp.data["total_vagas"] == 0
    assert resp.data["dres"] == []


def test_filter_cargo_codigo_sozinho(api_client, escola_1, escola_2):
    """Verifica filter cargo codigo sozinho."""
    url = reverse("vagas-escolas-list")
    p1 = uuid4()
    api_client.post(url, payload(p1, eol1="123456"), format="json")
    p2 = uuid4()
    api_client.post(url, payload(p2, eol1="789012"), format="json")
    resp = api_client.get(url, {"cargo_codigo": 123})
    assert resp.status_code == 200
    assert len(resp.data.get("vagas", [])) >= 2
    assert resp.data["total_vagas"] >= 10


def test_filter_por_processo_uuid_e_cargo_codigo(
    api_client, escola_1, escola_2
):
    """Verifica filter por processo uuid e cargo codigo."""
    url = reverse("vagas-escolas-list")
    p_uuid = uuid4()
    api_client.post(
        url, payload(p_uuid, eol1="123456", eol2="789012"), format="json"
    )
    api_client.post(url, payload(p_uuid, eol1="123456"), format="json")
    resp_123 = api_client.get(
        url, {"processo_uuid": str(p_uuid), "cargo_codigo": 123}
    )
    assert resp_123.status_code == 200
    vagas_123 = resp_123.data.get("vagas", [])
    assert len(vagas_123) == 1
    assert vagas_123[0]["cargo_codigo"] == 123
    assert resp_123.data["total_vagas"] == 5
    resp_456 = api_client.get(
        url, {"processo_uuid": str(p_uuid), "cargo_codigo": 456}
    )
    assert resp_456.status_code == 200
    vagas_456 = resp_456.data.get("vagas", [])
    assert len(vagas_456) == 0
    assert resp_456.data["total_vagas"] == 0


def test_create_retorna_400_quando_tipo_ue_desabilitado(api_client):
    """Verifica create retorna 400 quando tipo ue desabilitado."""
    url = reverse("vagas-escolas-list")
    p_uuid = uuid4()
    body = {
        "processo_uuid": str(p_uuid),
        "processo_nome": "Proc",
        "vagas": [
            {
                "data_fechamento_modulo": "2025-09-10",
                "cargo_codigo": 123,
                "cargo_descricao": "Professor",
                "codigo_eol": "123456",
                "vagas_precarias": 0,
                "vagas_definitivas": 1,
                "status": "ativo",
            }
        ],
    }
    with patch(
        "vagas_escolas.api.views.vagas_escolas.processar_criacao_vagas_lote",
        side_effect=TipoUEDesabilitadoException("Tipo UE bloqueado"),
    ):
        resp = api_client.post(url, body, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data.get("code") == "TIPO_UE_DESABILITADO"
    assert "Tipo UE bloqueado" in resp.data.get("detail", "")


def test_create_retorna_500_quando_excecao_generica(api_client):
    """Verifica create retorna 500 quando excecao generica."""
    url = reverse("vagas-escolas-list")
    p_uuid = uuid4()
    body = {
        "processo_uuid": str(p_uuid),
        "processo_nome": "Proc",
        "vagas": [
            {
                "data_fechamento_modulo": "2025-09-10",
                "cargo_codigo": 123,
                "cargo_descricao": "Professor",
                "codigo_eol": "123456",
                "vagas_precarias": 0,
                "vagas_definitivas": 1,
                "status": "ativo",
            }
        ],
    }
    with patch(
        "vagas_escolas.api.views.vagas_escolas.processar_criacao_vagas_lote",
        side_effect=Exception("falha inesperada"),
    ):
        resp = api_client.post(url, body, format="json")
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.data.get("code") == "ERRO_AO_CRIAR_VAGAS_EM_LOTE"
    assert "falha inesperada" in resp.data.get("detail", "")
