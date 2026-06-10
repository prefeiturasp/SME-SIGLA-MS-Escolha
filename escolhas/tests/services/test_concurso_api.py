"""Testes unitários para ConcursoAPIService."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import requests

from escolhas.services.concurso_api import ConcursoAPIService


class TestConcursoAPIService:
    """Testes para ConcursoAPIService."""

    def test_buscar_concurso_uuid_sucesso(self, settings: Any) -> None:
        """Verifica buscar concurso uuid sucesso."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response_data = {"uuid": concurso_uuid, "nome": "Concurso Teste"}
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result == concurso_uuid
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert (
                call_args[0][0]
                == f"http://test-api.com/api/v1/concursos/{concurso_uuid}/"
            )
            assert call_args[1]["timeout"] == 30

    def test_buscar_concurso_uuid_nao_encontrado(self, settings: Any) -> None:
        """Verifica buscar concurso uuid nao encontrado."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response_data = {"uuid": None, "nome": "Concurso Teste"}
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_http_error_404(self, settings: Any) -> None:
        """Verifica buscar concurso uuid http error 404."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError(
                "404 Not Found"
            )
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_http_error_500(self, settings: Any) -> None:
        """Verifica buscar concurso uuid http error 500."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError(
                "500 Internal Server Error"
            )
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_connection_error(
        self, settings: Any
    ) -> None:
        """Verifica buscar concurso uuid connection error."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError(
                "Connection failed"
            )
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_timeout(self, settings: Any) -> None:
        """Verifica buscar concurso uuid timeout."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout(
                "Request timeout"
            )
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_excecao_generica(
        self, settings: Any
    ) -> None:
        """Verifica buscar concurso uuid excecao generica."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = Exception("Erro genérico")
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_resposta_sem_uuid(
        self, settings: Any
    ) -> None:
        """Verifica buscar concurso uuid resposta sem uuid."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        concurso_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_response_data = {"nome": "Concurso Teste"}
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            assert result is None

    def test_buscar_concurso_uuid_metodo_estatico(self) -> None:
        """Verifica buscar concurso uuid metodo estatico."""
        import inspect

        assert (
            inspect.ismethod(ConcursoAPIService.buscar_concurso_uuid) is False
        )
        assert hasattr(ConcursoAPIService, "buscar_concurso_uuid")

    def test_get_cargos_por_codigos_sucesso(self, settings: Any) -> None:
        """Verifica get cargos por codigos sucesso."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        mock_response_data = [{"codigo": "10", "nome": "Professor"}]
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            result = ConcursoAPIService.get_cargos_por_codigos(["10"])
            assert result == {"10": "Professor"}

    def test_get_cargos_por_codigos_lista_vazia(self, settings: Any) -> None:
        """Verifica get cargos por codigos lista vazia."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            result = ConcursoAPIService.get_cargos_por_codigos([])
            assert result == {}
            mock_get.assert_not_called()

    def test_get_cargos_por_codigos_sem_url(self, settings: Any) -> None:
        """Verifica get cargos por codigos sem url."""
        settings.CONCURSOS_API_URL = ""
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            result = ConcursoAPIService.get_cargos_por_codigos(["10"])
            assert result == {}
            mock_get.assert_not_called()

    def test_get_cargos_por_codigos_erro_http(self, settings: Any) -> None:
        """Verifica get cargos por codigos erro http."""
        settings.CONCURSOS_API_URL = "http://test-api.com"
        with patch("sigla_sdk.http.api_client.http_client.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("err")
            result = ConcursoAPIService.get_cargos_por_codigos(["10"])
            assert result == {}
