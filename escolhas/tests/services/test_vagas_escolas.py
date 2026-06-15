"""Módulo tests/services/test_vagas_escolas."""

from __future__ import annotations

from uuid import uuid4

import pytest
from rest_framework import status

from escolhas.models import Parametrizacao, VagasEscolas, VagasEscolasLote
from escolhas.services.exceptions import TipoUEDesabilitadoException
from escolhas.services.vagas_escolas import (
    atualizar_vagas_utilizadas_por_processo,
    criar_vagas_em_lote,
    processar_criacao_vagas_lote,
)


@pytest.mark.django_db
class TestCriarVagasEmLote:
    """Testes para a função criar_vagas_em_lote."""

    def test_criar_vagas_em_lote_sucesso(self, escola_1, vaga_data_valida):
        """Verifica criar vagas em lote sucesso."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        created_vagas, errors = criar_vagas_em_lote([vaga_data_valida], lote)
        assert len(created_vagas) == 1
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_1
        assert created_vagas[0].lote == lote

    def test_criar_vagas_em_lote_multiplas_sucesso(
        self, escola_1, escola_2, vagas_data_multiplas
    ):
        """Verifica criar vagas em lote multiplas sucesso."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        created_vagas, errors = criar_vagas_em_lote(vagas_data_multiplas, lote)
        assert len(created_vagas) == 2
        assert len(errors) == 0
        assert created_vagas[0].escola == escola_1
        assert created_vagas[1].escola == escola_2

    def test_criar_vagas_em_lote_escola_nao_encontrada(self, vaga_data_valida):
        """Verifica criar vagas em lote escola nao encontrada."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        vaga = {**vaga_data_valida, "codigo_eol": "999999"}
        created_vagas, errors = criar_vagas_em_lote([vaga], lote)
        assert len(created_vagas) == 0
        assert len(errors) == 1

    def test_criar_vagas_em_lote_mistura_sucesso_erro(
        self, escola_1, vaga_data_valida
    ):
        """Verifica criar vagas em lote mistura sucesso erro."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        vagas_data = [
            vaga_data_valida,
            {
                "data_fechamento_modulo": "2025-09-15",
                "cargo_codigo": 456,
                "cargo_descricao": "Professor de Português",
                "codigo_eol": "999999",
                "vagas_precarias": 1,
                "vagas_definitivas": 2,
                "status": "ativo",
            },
        ]
        created_vagas, errors = criar_vagas_em_lote(vagas_data, lote)
        assert len(created_vagas) == 1
        assert len(errors) == 1
        assert created_vagas[0].escola == escola_1
        assert errors[0]["vaga_index"] == 2

    def test_criar_vagas_em_lote_dados_invalidos(self, escola_1):
        """Verifica criar vagas em lote dados invalidos."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        vaga_data = {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": "123456",
            "vagas_precarias": "texto_invalido",
            "vagas_definitivas": 3,
            "status": "ativo",
        }
        created_vagas, errors = criar_vagas_em_lote([vaga_data], lote)
        assert len(created_vagas) == 0
        assert len(errors) == 1
        assert errors[0]["vaga_index"] == 1
        assert "Erro ao criar vaga" in errors[0]["error"]


@pytest.mark.django_db
class TestProcessarCriacaoVagasLote:
    """Testes para a função processar_criacao_vagas_lote."""

    def test_processar_criacao_sucesso(
        self, escola_1, escola_2, request_data_valido
    ):
        """Verifica processar criacao sucesso."""
        response_data, status_code = processar_criacao_vagas_lote(
            request_data_valido
        )
        assert status_code == status.HTTP_201_CREATED
        assert response_data["vagas_criadas"] == 2
        assert "lote_uuid" in response_data
        assert "processo_uuid" in response_data
        assert (
            VagasEscolas.objects.filter(
                lote__uuid=response_data["lote_uuid"]
            ).count()
            == 2
        )

    def test_processar_criacao_dados_invalidos(self, request_data_invalido):
        """Verifica processar criacao dados invalidos."""
        response_data, status_code = processar_criacao_vagas_lote(
            request_data_invalido
        )
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_lista_vazia(self, request_data_vazio):
        """Verifica processar criacao lista vazia."""
        response_data, status_code = processar_criacao_vagas_lote(
            request_data_vazio
        )
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_escolas_nao_encontradas(self):
        """Verifica processar criacao escolas nao encontradas."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor de Matemática",
                    "codigo_eol": "999999",
                    "vagas_precarias": 2,
                    "vagas_definitivas": 3,
                    "status": "ativo",
                }
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert response_data["vagas_criadas"] == 0
        assert response_data["total_processadas"] == 1
        assert "erros" in response_data
        assert response_data["vagas_com_erro"] == 1

    def test_processar_criacao_mistura_sucesso_erro(self, escola_1):
        """Verifica processar criacao mistura sucesso erro."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
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
                    "status": "ativo",
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "999999",
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo",
                },
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_207_MULTI_STATUS
        assert response_data["vagas_criadas"] == 1
        assert response_data["total_processadas"] == 2
        assert "erros" in response_data
        assert response_data["vagas_com_erro"] == 1

    def test_processar_criacao_campos_obrigatorios_faltando(self):
        """Verifica processar criacao campos obrigatorios faltando."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
            "vagas": [
                {"data_fechamento_modulo": "2025-09-10", "cargo_codigo": 123}
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_bloqueia_por_parametrizacao_tipo_ue(
        self, escola_1
    ):
        """Verifica processar criacao bloqueia por parametrizacao tipo ue."""
        escola_1.tipo_ue = "EMEF"
        escola_1.save(update_fields=["tipo_ue"])
        Parametrizacao.objects.create(tipo_ue="EMEF", usar=False)
        request_data = {
            "processo_uuid": str(uuid4()),
            "processo_nome": "Proc",
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor",
                    "codigo_eol": escola_1.codigo_eol,
                    "vagas_precarias": 0,
                    "vagas_definitivas": 1,
                    "status": "ativo",
                }
            ],
        }
        with pytest.raises(TipoUEDesabilitadoException):
            processar_criacao_vagas_lote(request_data)

    def test_processar_criacao_ignora_escola_inexistente_na_validacao(self):
        """Verifica processar criacao ignora escola inexistente na validacao."""
        Parametrizacao.objects.create(tipo_ue="EMEF", usar=False)
        request_data = {
            "processo_uuid": str(uuid4()),
            "processo_nome": "Proc",
            "vagas": [
                {
                    "data_fechamento_modulo": "2025-09-10",
                    "cargo_codigo": 123,
                    "cargo_descricao": "Professor",
                    "codigo_eol": "999999",
                    "vagas_precarias": 0,
                    "vagas_definitivas": 1,
                    "status": "ativo",
                }
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert response_data.get("vagas_criadas") == 0
        assert response_data.get("vagas_com_erro") == 1

    def test_processar_criacao_chave_vagas_faltando(self):
        """Verifica processar criacao chave vagas faltando."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        request_data = {
            "processo_uuid": str(lote.processo_uuid),
            "processo_nome": lote.processo_nome,
            "outros_dados": "valor",
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data

    def test_processar_criacao_processo_uuid_invalido_retorna_mensagem_em_portugues(
        self,
    ):
        """Verifica processar criacao processo uuid invalido retorna mensagem em portugues."""
        request_data = {
            "processo_uuid": "uuid-invalido",
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
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response_data
        assert "processo_uuid" in response_data["errors"]
        assert (
            response_data["errors"]["processo_uuid"][0]
            == "Deve ser um UUID válido."
        )

    def test_processar_criacao_mesmo_processo_duas_vezes_cria_lotes_distintos(
        self, escola_1, escola_2, vagas_data_multiplas
    ):
        """Verifica processar criacao mesmo processo duas vezes cria lotes distintos."""
        proc_uuid = uuid4()
        req1 = {
            "processo_uuid": str(proc_uuid),
            "processo_nome": "P1",
            "vagas": vagas_data_multiplas,
        }
        req2 = {
            "processo_uuid": str(proc_uuid),
            "processo_nome": "P2",
            "vagas": [vagas_data_multiplas[0]],
        }
        r1, s1 = processar_criacao_vagas_lote(req1)
        r2, s2 = processar_criacao_vagas_lote(req2)
        assert s1 in (201, 207) and s2 in (201, 207)
        lotes = list(
            VagasEscolasLote.objects.filter(processo_uuid=proc_uuid).order_by(
                "criado_em"
            )
        )
        assert len(lotes) == 2
        assert VagasEscolas.objects.filter(lote=lotes[-1]).count() == 1

    def test_processar_criacao_zfill_codigo_eol(
        self, escola_1, vagas_data_multiplas
    ):
        """Verifica processar criacao zfill codigo eol."""
        escola_1.codigo_eol = "000123"
        escola_1.save(update_fields=["codigo_eol"])
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
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
        """Verifica fluxo completo criacao vagas."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
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
                    "status": "ativo",
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "789012",
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo",
                },
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == status.HTTP_201_CREATED
        assert response_data["vagas_criadas"] == 2
        vagas_criadas = VagasEscolas.objects.all()
        assert vagas_criadas.count() == 2
        vaga1 = vagas_criadas.filter(cargo_codigo=123).first()
        vaga2 = vagas_criadas.filter(cargo_codigo=456).first()
        assert vaga1.escola == escola_1
        assert vaga2.escola == escola_2
        assert vaga1.cargo_descricao == "Professor de Matemática"
        assert vaga2.cargo_descricao == "Professor de Português"


@pytest.mark.django_db
class TestAtualizarVagasUtilizadasPorProcesso:
    """Representa TestAtualizarVagasUtilizadasPorProcesso."""

    def test_atualizar_vagas_utilizadas_sucesso(self, escola_1):
        """Verifica atualizar vagas utilizadas sucesso."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        v1 = VagasEscolas.objects.create(
            escola=escola_1,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=100,
            cargo_descricao="Cargo 1",
            vagas_precarias=3,
            vagas_definitivas=2,
            status="1",
        )
        v2 = VagasEscolas.objects.create(
            escola=escola_1,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=101,
            cargo_descricao="Cargo 2",
            vagas_precarias=1,
            vagas_definitivas=4,
            status="1",
        )
        result = atualizar_vagas_utilizadas_por_processo(
            vagas=[
                {"uuid": str(v1.uuid), "vagas_precarias_utilizadas": 2},
                {"uuid": str(v2.uuid), "vagas_definitivas_utilizadas": 3},
            ]
        )
        assert result["total"] == 2
        assert set(result["atualizados"]) == {str(v1.uuid), str(v2.uuid)}
        v1.refresh_from_db()
        v2.refresh_from_db()
        assert v1.vagas_precarias_utilizadas == 2
        assert v2.vagas_definitivas_utilizadas == 3

    def test_atualizar_vagas_utilizadas_lote_nao_encontrado(self):
        """Verifica atualizar vagas utilizadas lote nao encontrado."""
        result = atualizar_vagas_utilizadas_por_processo(vagas=[])
        assert result["total"] == 0
        assert result["atualizados"] == []
        assert result["nao_encontrados"] == []

    def test_atualizar_vagas_utilizadas_nao_encontrados(self, escola_1):
        """Verifica atualizar vagas utilizadas nao encontrados."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
        v1 = VagasEscolas.objects.create(
            escola=escola_1,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=100,
            cargo_descricao="Cargo 1",
            vagas_precarias=3,
            vagas_definitivas=2,
            status="1",
        )
        uuid_inexistente = str(uuid4())
        result = atualizar_vagas_utilizadas_por_processo(
            vagas=[
                {"uuid": str(v1.uuid), "vagas_definitivas_utilizadas": 1},
                {"uuid": uuid_inexistente, "vagas_precarias_utilizadas": 1},
            ]
        )
        assert result["total"] == 1
        assert result["nao_encontrados"] == [uuid_inexistente]
        v1.refresh_from_db()
        assert v1.vagas_definitivas_utilizadas == 1

    def test_rollback_em_caso_de_erro(self, escola_1):
        """Verifica rollback em caso de erro."""
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid4(), processo_nome="Proc"
        )
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
                    "status": "ativo",
                },
                {
                    "data_fechamento_modulo": "2025-09-15",
                    "cargo_codigo": 456,
                    "cargo_descricao": "Professor de Português",
                    "codigo_eol": "999999",
                    "vagas_precarias": 1,
                    "vagas_definitivas": 2,
                    "status": "ativo",
                },
            ],
        }
        response_data, status_code = processar_criacao_vagas_lote(request_data)
        assert status_code == 207
        assert response_data["vagas_criadas"] == 1
        vagas_criadas = VagasEscolas.objects.all()
        assert vagas_criadas.count() == 1
        assert vagas_criadas.first().cargo_codigo == 123
