"""Testes unitários para CandidatoAPIService."""

from __future__ import annotations

from unittest.mock import Mock, patch

import requests

from escolhas.services.candidato_api import CandidatoAPIService


class TestCandidatoAPIService:
    """Testes para CandidatoAPIService."""

    def test_init_com_base_url_personalizada(self):
        """Verifica init com base url personalizada."""
        service = CandidatoAPIService(
            base_url="http://custom-url.com", timeout_seconds=60
        )
        assert service.base_url == "http://custom-url.com"
        assert service.timeout_seconds == 60

    def test_init_sem_base_url_usando_settings(self, settings):
        """Verifica init sem base url usando settings."""
        settings.CANDIDATOS_API_URL = "http://default-url.com"
        service = CandidatoAPIService()
        assert service.base_url == "http://default-url.com"
        assert service.timeout_seconds == 30

    def test_init_remove_barra_final(self):
        """Verifica init remove barra final."""
        service = CandidatoAPIService(base_url="http://test.com/")
        assert service.base_url == "http://test.com"

    def test_buscar_candidatos_por_cpfs_sucesso(self, settings):
        """Verifica buscar candidatos por cpfs sucesso."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901", "98765432100"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response_data = [
            {
                "uuid": "candidato-uuid-1",
                "cpf": "12345678901",
                "nome": "Candidato 1",
            },
            {
                "uuid": "candidato-uuid-2",
                "cpf": "98765432100",
                "nome": "Candidato 2",
            },
        ]
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result == mock_response_data
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert (
                call_args[0][0]
                == "http://test-api.com/api/v1/habilitados/buscar-por-cpfs/"
            )
            assert call_args[1]["json"] == {
                "processo_uuid": processo_uuid,
                "cpfs": cpfs,
            }
            assert "Accept" in call_args[1]["headers"]
            assert "Content-Type" in call_args[1]["headers"]

    def test_buscar_candidatos_por_cpfs_lista_vazia(self, settings):
        """Verifica buscar candidatos por cpfs lista vazia."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = []
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response_data = []
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result == mock_response_data

    def test_buscar_candidatos_por_cpfs_http_error(self, settings):
        """Verifica buscar candidatos por cpfs http error."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_post.side_effect = requests.exceptions.HTTPError(
                "404 Not Found"
            )
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result is None

    def test_buscar_candidatos_por_cpfs_connection_error(self, settings):
        """Verifica buscar candidatos por cpfs connection error."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError(
                "Connection failed"
            )
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result is None

    def test_buscar_candidatos_por_cpfs_timeout(self, settings):
        """Verifica buscar candidatos por cpfs timeout."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout(
                "Request timeout"
            )
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result is None

    def test_buscar_candidatos_por_cpfs_excecao_generica(self, settings):
        """Verifica buscar candidatos por cpfs excecao generica."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_post.side_effect = Exception("Erro genérico")
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            assert result is None

    def test_buscar_candidatos_por_cpfs_timeout_personalizado(self, settings):
        """Verifica buscar candidatos por cpfs timeout personalizado."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService(timeout_seconds=60)
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            call_args = mock_post.call_args
            assert call_args[1]["timeout"] == 60

    def test_buscar_candidatos_por_cpfs_headers_corretos(self, settings):
        """Verifica buscar candidatos por cpfs headers corretos."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        cpfs = ["12345678901"]
        processo_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            call_args = mock_post.call_args
            headers = call_args[1]["headers"]
            assert headers["Accept"] == "application/json"
            assert headers["Content-Type"] == "application/json"

    def test_buscar_candidatos_sucesso(self, settings):
        """Verifica buscar candidatos sucesso."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        mock_response_data = [
            {"nome": "João", "cpf": "12345678901", "concursos": []}
        ]
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = service.buscar_candidatos(nome="João")
            assert result == mock_response_data
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert (
                call_args[0][0]
                == "http://test-api.com/api/v1/candidatos/buscar/"
            )
            assert call_args[1]["params"] == {"nome": "João"}
            assert "Accept" in call_args[1]["headers"]

    def test_buscar_candidatos_sem_parametros_retorna_lista_vazia(
        self, settings
    ):
        """Verifica buscar candidatos sem parametros retorna lista vazia."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            result = service.buscar_candidatos()
            assert result == []
            mock_get.assert_not_called()

    def test_buscar_candidatos_envia_params_corretos(self, settings):
        """Verifica buscar candidatos envia params corretos."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            service.buscar_candidatos(
                nome="Maria",
                cpf="11122233344",
                rg="12.345.678-9",
                registro_funcional="RF001",
            )
            call_args = mock_get.call_args
            assert call_args[1]["params"] == {
                "nome": "Maria",
                "cpf": "11122233344",
                "rg": "12.345.678-9",
                "registro_funcional": "RF001",
            }

    def test_buscar_candidatos_http_error_retorna_none(self, settings):
        """Verifica buscar candidatos http error retorna none."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError(
                "502 Bad Gateway"
            )
            result = service.buscar_candidatos(nome="Teste")
            assert result is None

    def test_buscar_candidatos_connection_error_retorna_none(self, settings):
        """Verifica buscar candidatos connection error retorna none."""
        settings.CANDIDATOS_API_URL = "http://test-api.com"
        service = CandidatoAPIService()
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            result = service.buscar_candidatos(cpf="123")
            assert result is None
