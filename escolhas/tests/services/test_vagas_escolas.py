import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import status

from escolhas.models import VagasEscolas, Escola, Dre
from escolhas.services.vagas_escolas import (
    criar_vagas_em_lote,
    processar_criacao_vagas_lote
)

@pytest.fixture
@pytest.mark.django_db
def dre_teste():
    """Fixture para criar uma DRE de teste."""
    return Dre.objects.create(
        codigo="123456",
        nome="DRE Teste",
        sigla="DRE-TESTE"
    )


@pytest.fixture
@pytest.mark.django_db
def escola_teste(dre_teste):
    """Fixture para criar uma escola de teste."""
    return Escola.objects.create(
        dre=dre_teste,
        codigo_eol="123456",
        nome_oficial="Escola Teste",
        nome_nao_oficial="Escola Teste",
        tipo_unidade_admin="EMEF",
        tipo_ue="EMEF",
        logradouro="Rua Teste",
        numero="123",
        bairro="Bairro Teste",
        cep=12345678,
        distrito="Distrito Teste",
        sub_prefeitura="Subprefeitura Teste",
        nome_dre="DRE Teste",
        email="teste@escola.com",
        telefone1="(11) 1234-5678",
        telefone2="(11) 8765-4321",
        ano_construcao=2020,
        propriedade="Municipal",
        capacidade_vagas_matutino=100,
        capacidade_vagas_vespertino=100,
        capacidade_vagas_noturno=50,
        capacidade_vagas_intermediario=50,
        capacidade_vagas_integral=200,
        capacidade_vagas_total=500,
        organizacao_parceira=False,
        quantidade_de_funcionarios=20,
        status="ativo"
    )


@pytest.fixture
@pytest.mark.django_db
def escola_teste_2(dre_teste):
    """Fixture para criar uma segunda escola de teste."""
    return Escola.objects.create(
        dre=dre_teste,
        codigo_eol="789012",
        nome_oficial="Escola Teste 2",
        nome_nao_oficial="Escola Teste 2",
        tipo_unidade_admin="EMEF",
        tipo_ue="EMEF",
        logradouro="Rua Teste 2",
        numero="456",
        bairro="Bairro Teste 2",
        cep=12345678,
        distrito="Distrito Teste",
        sub_prefeitura="Subprefeitura Teste",
        nome_dre="DRE Teste",
        email="teste2@escola.com",
        telefone1="(11) 1111-1111",
        telefone2="(11) 2222-2222",
        ano_construcao=2021,
        propriedade="Municipal",
        capacidade_vagas_matutino=150,
        capacidade_vagas_vespertino=150,
        capacidade_vagas_noturno=75,
        capacidade_vagas_intermediario=75,
        capacidade_vagas_integral=300,
        capacidade_vagas_total=750,
        organizacao_parceira=False,
        quantidade_de_funcionarios=30,
        status="ativo"
    )


@pytest.fixture
def vaga_data_valida():
    """Fixture para dados válidos de vaga."""
    return {
        "data_fechamento_modulo": "2025-09-10",
        "cargo_codigo": 123,
        "cargo_descricao": "Professor de Matemática",
        "codigo_eol": "123456",
        "vagas_precarias": 2,
        "vagas_definitivas": 3,
        "status": "ativo"
    }


@pytest.fixture
def vagas_data_multiplas():
    """Fixture para múltiplas vagas válidas."""
    return [
        {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": "123456",
            "vagas_precarias": 2,
            "vagas_definitivas": 3,
            "status": "ativo"
        },
        {
            "data_fechamento_modulo": "2025-09-15",
            "cargo_codigo": 456,
            "cargo_descricao": "Professor de Português",
            "codigo_eol": "789012",
            "vagas_precarias": 1,
            "vagas_definitivas": 2,
            "status": "ativo"
        }
    ]


@pytest.fixture
def request_data_valido(vagas_data_multiplas):
    """Fixture para dados de requisição válidos."""
    return {
        "vagas": vagas_data_multiplas
    }


@pytest.fixture
def request_data_invalido():
    """Fixture para dados de requisição inválidos."""
    return {
        "vagas": [
            {
                "data_fechamento_modulo": "2025-09-10",
                "cargo_codigo": 123,
                # Faltando campos obrigatórios
            }
        ]
    }


@pytest.fixture
def request_data_vazio():
    """Fixture para dados de requisição com lista vazia."""
    return {
        "vagas": []
    }


@pytest.mark.django_db
class TestCriarVagasEmLote:
    """Testes para a função criar_vagas_em_lote."""

    def test_criar_vagas_em_lote_sucesso(self, escola_teste, vaga_data_valida):
        """Testa criação bem-sucedida de uma vaga."""
        vagas_data = [vaga_data_valida]
        
        created_vagas, errors = criar_vagas_em_lote(vagas_data)
        
        assert len(created_vagas) == 1
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_teste
        assert created_vagas[0].cargo_codigo == 123
        assert created_vagas[0].cargo_descricao == "Professor de Matemática"

    def test_criar_vagas_em_lote_multiplas_sucesso(self, escola_teste, escola_teste_2, vagas_data_multiplas):
        """Testa criação bem-sucedida de múltiplas vagas."""
        created_vagas, errors = criar_vagas_em_lote(vagas_data_multiplas)
        
        assert len(created_vagas) == 2
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_teste
        assert created_vagas[1].escola == escola_teste_2

    def test_criar_vagas_em_lote_escola_nao_encontrada(self, vaga_data_valida):
        """Testa erro quando escola não é encontrada."""
        vaga_data = vaga_data_valida.copy()
        vaga_data["codigo_eol"] = "999999"  # Código EOL inexistente
        
        created_vagas, errors = criar_vagas_em_lote([vaga_data])
        
        assert len(created_vagas) == 0
        assert len(errors) == 1
        assert errors[0]["vaga_index"] == 1
        assert errors[0]["codigo_eol"] == "999999"
        assert "não encontrada" in errors[0]["error"]

    def test_criar_vagas_em_lote_mistura_sucesso_erro(self, escola_teste, vaga_data_valida):
        """Testa criação com algumas vagas bem-sucedidas e outras com erro."""
        vagas_data = [
            vaga_data_valida,  # Vaga válida
            {
                "data_fechamento_modulo": "2025-09-15",
                "cargo_codigo": 456,
                "cargo_descricao": "Professor de Português",
                "codigo_eol": "999999",  # Escola inexistente
                "vagas_precarias": 1,
                "vagas_definitivas": 2,
                "status": "ativo"
            }
        ]
        
        created_vagas, errors = criar_vagas_em_lote(vagas_data)
        
        assert len(created_vagas) == 1
        assert len(errors) == 1
        assert created_vagas[0].escola == escola_teste
        assert errors[0]["vaga_index"] == 2

    def test_criar_vagas_em_lote_dados_invalidos(self, escola_teste):
        """Testa erro com dados inválidos na criação da vaga."""
        vaga_data = {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": "123456",
            "vagas_precarias": "texto_invalido",  # Tipo inválido
            "vagas_definitivas": 3,
            "status": "ativo"
        }
        
        created_vagas, errors = criar_vagas_em_lote([vaga_data])
        
        assert len(created_vagas) == 0
        assert len(errors) == 1
        assert errors[0]["vaga_index"] == 1
        assert "Erro ao criar vaga" in errors[0]["error"]

    def test_criar_vagas_em_lote_transacao_atomica(self, escola_teste, vaga_data_valida):
        """Testa que a transação é atômica."""
        vagas_data = [vaga_data_valida]
        
        with patch('escolhas.services.vagas_escolas.transaction.atomic') as mock_atomic:
            mock_atomic.return_value.__enter__ = MagicMock()
            mock_atomic.return_value.__exit__ = MagicMock()
            
            criar_vagas_em_lote(vagas_data)
            
            mock_atomic.assert_called_once()


@pytest.mark.django_db
class TestProcessarCriacaoVagasLote:
    """Testes para a função processar_criacao_vagas_lote."""

    def test_processar_criacao_sucesso(self, escola_teste, escola_teste_2, request_data_valido):
        """Testa processamento bem-sucedido de criação em lote."""
        response_data, status_code = processar_criacao_vagas_lote(request_data_valido)
        
        assert status_code == status.HTTP_201_CREATED
        assert response_data["vagas_criadas"] == 2
        assert response_data["total_processadas"] == 2
        assert "vagas criadas com sucesso" in response_data["mensagem"]
        assert "erros" not in response_data

    def test_processar_criacao_dados_invalidos(self, request_data_invalido):
        """Testa processamento com dados inválidos."""
        response_data, status_code = processar_criacao_vagas_lote(request_data_invalido)
        
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_lista_vazia(self, request_data_vazio):
        """Testa processamento com lista vazia."""
        response_data, status_code = processar_criacao_vagas_lote(request_data_vazio)
        
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_escolas_nao_encontradas(self):
        """Testa processamento quando nenhuma escola é encontrada."""
        request_data = {
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "999999",  # Escola inexistente
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo"
                }
            ]
        }
        
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert response_data["vagas_criadas"] == 0
        assert response_data["total_processadas"] == 1
        assert "erros" in response_data
        assert response_data["vagas_com_erro"] == 1

    def test_processar_criacao_mistura_sucesso_erro(self, escola_teste):
        """Testa processamento com algumas vagas bem-sucedidas e outras com erro."""
        request_data = {
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "123456",  # Escola existente
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo"
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "999999",  # Escola inexistente
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo"
                }
            ]
        }
        
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        assert status_code == status.HTTP_207_MULTI_STATUS
        assert response_data["vagas_criadas"] == 1
        assert response_data["total_processadas"] == 2
        assert "erros" in response_data
        assert response_data["vagas_com_erro"] == 1

    def test_processar_criacao_campos_obrigatorios_faltando(self):
        """Testa processamento com campos obrigatórios faltando."""
        request_data = {
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    # Faltando cargo_descricao, codigo_eol, vagas_precarias, vagas_definitivas, status
                }
            ]
        }
        
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_chave_vagas_faltando(self):
        """Testa processamento sem a chave 'vagas'."""
        request_data = {
            "outros_dados": "valor"
        }
        
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data


@pytest.mark.django_db
class TestIntegracaoVagasEscolas:
    """Testes de integração para o service de vagas das escolas."""

    def test_fluxo_completo_criacao_vagas(self, escola_teste, escola_teste_2):
        """Testa o fluxo completo de criação de vagas."""
        request_data = {
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "123456",
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo"
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "789012",
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo"
                }
            ]
        }
        
        # Processa a criação
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        # Verifica resposta
        assert status_code == status.HTTP_201_CREATED
        assert response_data["vagas_criadas"] == 2
        
        # Verifica se as vagas foram realmente criadas no banco
        vagas_criadas = VagasEscolas.objects.all()
        assert vagas_criadas.count() == 2
        
        vaga1 = vagas_criadas.filter(cargo_codigo=123).first()
        vaga2 = vagas_criadas.filter(cargo_codigo=456).first()
        
        assert vaga1.escola == escola_teste
        assert vaga2.escola == escola_teste_2
        assert vaga1.cargo_descricao == "Professor de Matemática"
        assert vaga2.cargo_descricao == "Professor de Português"

    def test_rollback_em_caso_de_erro(self, escola_teste):
        """Testa que não há rollback quando algumas vagas são criadas com sucesso."""
        request_data = {
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "123456",  # Escola existente
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo"
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "999999",  # Escola inexistente
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo"
                }
            ]
        }
        
        # Processa a criação
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        
        # Verifica que uma vaga foi criada mesmo com erro na outra
        assert status_code == 207
        assert response_data["vagas_criadas"] == 1
        
        # Verifica se a vaga válida foi criada no banco
        vagas_criadas = VagasEscolas.objects.all()
        assert vagas_criadas.count() == 1
        assert vagas_criadas.first().cargo_codigo == 123
