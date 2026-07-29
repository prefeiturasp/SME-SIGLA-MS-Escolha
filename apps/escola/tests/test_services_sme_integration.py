"""Módulo tests/services/test_sme_integration."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from escola.services import (
    buscar_dados_escola_por_eol,
    buscar_dres_de_smeintegracao,
    buscar_ues_codigos_por_dre,
)


def _setup_settings(settings):
    """Setup settings."""
    settings.SMEINTEGRACAO_API_URL = "https://api.example.com"
    settings.SMEINTEGRACAO_API_TOKEN = "token"


def test_buscar_dres_de_smeintegracao_happy(settings):
    """Verifica buscar dres de smeintegracao happy."""
    _setup_settings(settings)
    payload = [
        {"codigoDRE": "108100", "nomeDRE": "DRE BT", "siglaDRE": "DRE - BT"},
        {"codigoDRE": "108200", "nomeDRE": "DRE IP", "siglaDRE": "DRE - IP"},
    ]
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = buscar_dres_de_smeintegracao()
        assert len(result) == 2
        assert result[0]["codigo"] == "108100"
        assert result[0]["nome"] == "DRE BT"
        assert result[0]["sigla"] == "DRE - BT"


def test_buscar_ues_codigos_por_dre_happy(settings):
    """Verifica buscar ues codigos por dre happy."""
    _setup_settings(settings)
    payload = ["400292", "307306"]
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = buscar_ues_codigos_por_dre("108100")
        assert result == ["400292", "307306"]


def test_buscar_dados_escola_por_eol_happy(settings):
    """Verifica buscar dados escola por eol happy."""
    _setup_settings(settings)
    payload = {"codigo": "400292", "nome": "ESCOLA X"}
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = buscar_dados_escola_por_eol("400292")
        assert result["codigo"] == "400292"
        assert result["nome"] == "ESCOLA X"


def test_buscar_dres_de_smeintegracao_erros_de_config(settings):
    """Verifica buscar dres de smeintegracao erros de config."""
    settings.SMEINTEGRACAO_API_URL = None
    settings.SMEINTEGRACAO_API_TOKEN = None
    with pytest.raises(ValueError):
        buscar_dres_de_smeintegracao()


def test_buscar_dres_formato_invalido(settings):
    """Verifica buscar dres formato invalido."""
    _setup_settings(settings)
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {"unexpected": True}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(ValueError):
            buscar_dres_de_smeintegracao()


def test_buscar_dres_http_error(settings):
    """Verifica buscar dres http error."""
    _setup_settings(settings)
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("boom")
        mock_get.return_value = mock_resp
        with pytest.raises(requests.HTTPError):
            buscar_dres_de_smeintegracao()


def test_buscar_ues_formato_invalido(settings):
    """Verifica buscar ues formato invalido."""
    _setup_settings(settings)
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = {"items": []}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(ValueError):
            buscar_ues_codigos_por_dre("108100")


def test_buscar_escola_formato_invalido(settings):
    """Verifica buscar escola formato invalido."""
    _setup_settings(settings)
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = [1, 2]
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        with pytest.raises(ValueError):
            buscar_dados_escola_por_eol("400292")


def test_buscar_escola_http_error(settings):
    """Verifica buscar escola http error."""
    _setup_settings(settings)
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("err")
        mock_get.return_value = mock_resp
        with pytest.raises(requests.HTTPError):
            buscar_dados_escola_por_eol("400292")


def test_buscar_dres_de_smeintegracao_sem_token(settings):
    """Verifica buscar dres de smeintegracao sem token."""
    settings.SMEINTEGRACAO_API_URL = "https://api.example.com"
    settings.SMEINTEGRACAO_API_TOKEN = None
    with pytest.raises(ValueError) as exc:
        buscar_dres_de_smeintegracao()
    assert "SMEINTEGRACAO_API_TOKEN" in str(exc.value)


def test_buscar_dres_ignora_itens_nao_dict(settings):
    """Verifica buscar dres ignora itens nao dict."""
    _setup_settings(settings)
    payload = [
        None,
        "invalid",
        123,
        {"codigoDRE": "108100", "nomeDRE": "DRE BT", "siglaDRE": "DRE - BT"},
    ]
    with patch("escola.services.sme_integration.requests.get") as mock_get:
        mock_resp = Mock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp
        result = buscar_dres_de_smeintegracao()
        assert len(result) == 1
        assert result[0]["codigo"] == "108100"
        assert result[0]["nome"] == "DRE BT"
        assert result[0]["sigla"] == "DRE - BT"
