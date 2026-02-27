"""
Testes unitários para CandidatoAPIService.
"""
import pytest
from unittest.mock import patch, Mock
import requests
from django.conf import settings

from escolhas.services.candidato_api import CandidatoAPIService


class TestCandidatoAPIService:
    """Testes para CandidatoAPIService."""

    def test_init_com_base_url_personalizada(self):
        """Testa inicialização com base_url personalizada."""
        service = CandidatoAPIService(base_url='http://custom-url.com', timeout_seconds=60)
        assert service.base_url == 'http://custom-url.com'
        assert service.timeout_seconds == 60

    def test_init_sem_base_url_usando_settings(self, settings):
        """Testa inicialização sem base_url usando settings."""
        settings.CANDIDATOS_API_URL = 'http://default-url.com'
        service = CandidatoAPIService()
        assert service.base_url == 'http://default-url.com'
        assert service.timeout_seconds == 30

    def test_init_remove_barra_final(self):
        """Testa que remove barra final da URL."""
        service = CandidatoAPIService(base_url='http://test.com/')
        assert service.base_url == 'http://test.com'

    def test_buscar_candidatos_por_cpfs_sucesso(self, settings):
        """Testa busca de candidatos por CPFs com sucesso."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901', '98765432100']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        mock_response_data = [
            {
                'uuid': 'candidato-uuid-1',
                'cpf': '12345678901',
                'nome': 'Candidato 1'
            },
            {
                'uuid': 'candidato-uuid-2',
                'cpf': '98765432100',
                'nome': 'Candidato 2'
            }
        ]
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result == mock_response_data
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == 'http://test-api.com/api/v1/habilitados/buscar-por-cpfs/'
            assert call_args[1]['json'] == {
                'processo_uuid': processo_uuid,
                'cpfs': cpfs
            }
            assert 'Accept' in call_args[1]['headers']
            assert 'Content-Type' in call_args[1]['headers']

    def test_buscar_candidatos_por_cpfs_lista_vazia(self, settings):
        """Testa busca com lista de CPFs vazia."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = []
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        mock_response_data = []
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result == mock_response_data

    def test_buscar_candidatos_por_cpfs_http_error(self, settings):
        """Testa tratamento de erro HTTP."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.HTTPError('404 Not Found')
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result is None

    def test_buscar_candidatos_por_cpfs_connection_error(self, settings):
        """Testa tratamento de erro de conexão."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError('Connection failed')
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result is None

    def test_buscar_candidatos_por_cpfs_timeout(self, settings):
        """Testa tratamento de timeout."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout('Request timeout')
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result is None

    def test_buscar_candidatos_por_cpfs_excecao_generica(self, settings):
        """Testa tratamento de exceção genérica."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_post.side_effect = Exception('Erro genérico')
            
            result = service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            assert result is None

    def test_buscar_candidatos_por_cpfs_timeout_personalizado(self, settings):
        """Testa que usa timeout personalizado."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService(timeout_seconds=60)
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            call_args = mock_post.call_args
            assert call_args[1]['timeout'] == 60

    def test_buscar_candidatos_por_cpfs_headers_corretos(self, settings):
        """Testa que headers estão corretos."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()
        
        cpfs = ['12345678901']
        processo_uuid = '123e4567-e89b-12d3-a456-426614174000'
        
        with patch('escolhas.services.candidato_api.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            service.buscar_candidatos_por_cpfs(cpfs, processo_uuid)
            
            call_args = mock_post.call_args
            headers = call_args[1]['headers']
            assert headers['Accept'] == 'application/json'
            assert headers['Content-Type'] == 'application/json'

    # --- Testes de buscar_candidatos (feature/143715-consulta-concursado) ---

    def test_buscar_candidatos_sucesso(self, settings):
        """Testa busca de candidatos por nome/cpf/rg/registro_funcional com sucesso."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()

        mock_response_data = [
            {'nome': 'João', 'cpf': '12345678901', 'concursos': []},
        ]

        with patch('escolhas.services.candidato_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = service.buscar_candidatos(nome='João')

            assert result == mock_response_data
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == 'http://test-api.com/api/v1/candidatos/buscar/'
            assert call_args[1]['params'] == {'nome': 'João'}
            assert 'Accept' in call_args[1]['headers']

    def test_buscar_candidatos_sem_parametros_retorna_lista_vazia(self, settings):
        """Sem nenhum parâmetro informado, deve retornar lista vazia (não chama API)."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()

        with patch('escolhas.services.candidato_api.requests.get') as mock_get:
            result = service.buscar_candidatos()

            assert result == []
            mock_get.assert_not_called()

    def test_buscar_candidatos_envia_params_corretos(self, settings):
        """Testa que nome, cpf, rg e registro_funcional são enviados como query params."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()

        with patch('escolhas.services.candidato_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            service.buscar_candidatos(
                nome='Maria',
                cpf='11122233344',
                rg='12.345.678-9',
                registro_funcional='RF001',
            )

            call_args = mock_get.call_args
            assert call_args[1]['params'] == {
                'nome': 'Maria',
                'cpf': '11122233344',
                'rg': '12.345.678-9',
                'registro_funcional': 'RF001',
            }

    def test_buscar_candidatos_http_error_retorna_none(self, settings):
        """Em erro HTTP, deve retornar None."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()

        with patch('escolhas.services.candidato_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.HTTPError('502 Bad Gateway')

            result = service.buscar_candidatos(nome='Teste')

            assert result is None

    def test_buscar_candidatos_connection_error_retorna_none(self, settings):
        """Em erro de conexão, deve retornar None."""
        settings.CANDIDATOS_API_URL = 'http://test-api.com'
        service = CandidatoAPIService()

        with patch('escolhas.services.candidato_api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()

            result = service.buscar_candidatos(cpf='123')

            assert result is None

