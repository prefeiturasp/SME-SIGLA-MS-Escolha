"""
Testes unitários para ConcursoAPIService.
"""
import pytest
from unittest.mock import patch, Mock
import requests

from escolhas.services.concurso_api import ConcursoAPIService


class TestConcursoAPIService:
    """Testes para ConcursoAPIService."""

    def test_buscar_concurso_uuid_sucesso(self, settings):
        """Testa busca de concurso_uuid com sucesso."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        mock_response_data = {
            'uuid': concurso_uuid,
            'nome': 'Concurso Teste'
        }
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result == concurso_uuid
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == f'http://test-api.com/api/v1/concursos/{concurso_uuid}/'
            assert call_args[1]['timeout'] == 30

    def test_buscar_concurso_uuid_nao_encontrado(self, settings):
        """Testa quando concurso não é encontrado."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        mock_response_data = {
            'uuid': None,
            'nome': 'Concurso Teste'
        }
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_http_error_404(self, settings):
        """Testa tratamento de erro HTTP 404."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError('404 Not Found')
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_http_error_500(self, settings):
        """Testa tratamento de erro HTTP 500."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError('500 Internal Server Error')
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_connection_error(self, settings):
        """Testa tratamento de erro de conexão."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_timeout(self, settings):
        """Testa tratamento de timeout."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout('Request timeout')
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_excecao_generica(self, settings):
        """Testa tratamento de exceção genérica."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_get.side_effect = Exception('Erro genérico')
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_resposta_sem_uuid(self, settings):
        """Testa quando resposta não contém campo uuid."""
        settings.CONCURSOS_API_URL = 'http://test-api.com'
        concurso_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        mock_response_data = {
            'nome': 'Concurso Teste'
        }
        
        with patch('escolhas.services.concurso_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = ConcursoAPIService.buscar_concurso_uuid(concurso_uuid)
            
            assert result is None

    def test_buscar_concurso_uuid_metodo_estatico(self):
        """Testa que o método é estático."""
        import inspect
        assert inspect.ismethod(ConcursoAPIService.buscar_concurso_uuid) is False
        assert hasattr(ConcursoAPIService, 'buscar_concurso_uuid')

