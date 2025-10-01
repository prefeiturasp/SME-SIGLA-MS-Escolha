import pytest
from rest_framework import status
from uuid import uuid4

from escolhas.models import VagasEscolas, VagasEscolasLote
from escolhas.services.vagas_escolas import (
    criar_vagas_em_lote,
    processar_criacao_vagas_lote
)


@pytest.mark.django_db
class TestCriarVagasEmLote:
    """Testes para a função criar_vagas_em_lote."""

    def test_criar_vagas_em_lote_sucesso(self, escola_1, vaga_data_valida):
        """Testa criação bem-sucedida de uma vaga."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        created_vagas, errors = criar_vagas_em_lote([vaga_data_valida], lote)

        assert len(created_vagas) == 1
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_1
        assert created_vagas[0].lote == lote

    def test_criar_vagas_em_lote_multiplas_sucesso(self, escola_1, escola_2, vagas_data_multiplas):
        """Testa criação bem-sucedida de múltiplas vagas."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        created_vagas, errors = criar_vagas_em_lote(vagas_data_multiplas, lote)

        assert len(created_vagas) == 2
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_1
        assert created_vagas[1].escola == escola_2

    def test_criar_vagas_em_lote_escola_nao_encontrada(self, vaga_data_valida):
        """Testa erro quando escola não é encontrada."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        vaga = {**vaga_data_valida, "codigo_eol": "999999"}
        created_vagas, errors = criar_vagas_em_lote([vaga], lote)

        assert len(created_vagas) == 0
        assert len(errors) == 1

    def test_criar_vagas_em_lote_mistura_sucesso_erro(self, escola_1, vaga_data_valida):
        """Testa criação com algumas vagas bem-sucedidas e outras com erro."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
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

        created_vagas, errors = criar_vagas_em_lote(vagas_data, lote)

        assert len(created_vagas) == 1
        assert len(errors) == 1
        assert created_vagas[0].escola == escola_1
        assert errors[0]["vaga_index"] == 2

    def test_criar_vagas_em_lote_dados_invalidos(self, escola_1):
        """Testa erro com dados inválidos na criação da vaga."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        vaga_data = {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": "123456",
            "vagas_precarias": "texto_invalido",  # Tipo inválido
            "vagas_definitivas": 3,
            "status": "ativo"
        }
        
        created_vagas, errors = criar_vagas_em_lote([vaga_data], lote)
        
        assert len(created_vagas) == 0
        assert len(errors) == 1
        assert errors[0]["vaga_index"] == 1
        assert "Erro ao criar vaga" in errors[0]["error"]


@pytest.mark.django_db
class TestProcessarCriacaoVagasLote:
    """Testes para a função processar_criacao_vagas_lote."""

    def test_processar_criacao_sucesso(self, escola_1, escola_2, request_data_valido):
        """Testa processamento bem-sucedido de criação em lote."""
        response_data, status_code = processar_criacao_vagas_lote(request_data_valido)

        assert status_code == status.HTTP_201_CREATED
        assert response_data["vagas_criadas"] == 2
        assert "lote_uuid" in response_data
        assert "processo_uuid" in response_data
        # garante associação ao lote
        assert VagasEscolas.objects.filter(lote__uuid=response_data["lote_uuid"]).count() == 2

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
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
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

    def test_processar_criacao_mistura_sucesso_erro(self, escola_1):
        """Testa processamento com algumas vagas bem-sucedidas e outras com erro."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
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
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
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
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
            "outros_dados": "valor"
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)

        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data


    def test_processar_criacao_mesmo_processo_duas_vezes_cria_lotes_distintos(self, escola_1, escola_2, vagas_data_multiplas):
        """Testa processamento de um mesmo processo duas vezes, criando lotes distintos."""
        proc_uuid = uuid4()
        req1 = {"processo_uuid": str(proc_uuid), "processo_nome": "P1", "vagas": vagas_data_multiplas}
        req2 = {"processo_uuid": str(proc_uuid), "processo_nome": "P2", "vagas": [vagas_data_multiplas[0]]}
        r1, s1 = processar_criacao_vagas_lote(req1)
        r2, s2 = processar_criacao_vagas_lote(req2)
        assert s1 in (201, 207) and s2 in (201, 207)
        # dois lotes para o mesmo processo; último tem 1 vaga
        lotes = list(VagasEscolasLote.objects.filter(processo_uuid=proc_uuid).order_by('criado_em'))
        assert len(lotes) == 2
        assert VagasEscolas.objects.filter(lote=lotes[-1]).count() == 1

    def test_processar_criacao_zfill_codigo_eol(self, escola_1, vagas_data_multiplas):
        """Testa processamento de vagas com EOL zero-left."""
        # cria escola com EOL zero-left '000123' e envia vaga com '123'
        escola_1.codigo_eol = "000123"
        escola_1.save(update_fields=["codigo_eol"])
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
            "vagas": [{**vagas_data_multiplas[0], "codigo_eol": "123"}],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code in (201, 207)
        vaga = VagasEscolas.objects.first()
        assert vaga.escola.codigo_eol == "000123"


@pytest.mark.django_db
class TestIntegracaoVagasEscolas:
    """Testes de integração para o service de vagas das escolas."""

    def test_fluxo_completo_criacao_vagas(self, escola_1, escola_2):
        """Testa o fluxo completo de criação de vagas."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
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

        assert vaga1.escola == escola_1
        assert vaga2.escola == escola_2
        assert vaga1.cargo_descricao == "Professor de Matemática"
        assert vaga2.cargo_descricao == "Professor de Português"

    def test_rollback_em_caso_de_erro(self, escola_1):
        """Testa que não há rollback quando algumas vagas são criadas com sucesso."""
        lote = VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
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
