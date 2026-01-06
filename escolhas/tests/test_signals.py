import pytest
import uuid
from django.db import transaction

from escolhas.models import Escolha, VagasEscolas, VagasEscolasLote, Escola, Dre
from escolhas.choices import SituacaoChoices, TipoVagaChoices


@pytest.mark.django_db
class TestEscolhaSignals:
    """Testes para os signals de Escolha, especialmente a atualização de vagas restantes."""

    def test_signal_decrementa_vaga_definitiva_ao_criar_escolha(self):
        """Testa se o signal decrementa vagas_definitivas_restantes ao criar uma escolha."""
        # Setup
        dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
        escola = Escola.objects.create(
            codigo_eol="000001",
            nome_oficial="Escola Teste",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=100,
            cargo_descricao="Cargo Teste",
            vagas_precarias=3,
            vagas_precarias_restantes=3,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

        # Cria escolha (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

        # Verifica que a escolha foi criada
        assert escolha is not None

        # Verifica que a vaga foi decrementada
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial - 1
        # Verifica que vagas precárias não foram alteradas
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial

    def test_signal_decrementa_vaga_precaria_ao_criar_escolha(self):
        """Testa se o signal decrementa vagas_precarias_restantes ao criar uma escolha."""
        # Setup
        dre = Dre.objects.create(codigo="02", nome="DRE 02", sigla="DRE-02")
        escola = Escola.objects.create(
            codigo_eol="000002",
            nome_oficial="Escola Teste 2",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 2"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=101,
            cargo_descricao="Cargo Teste 2",
            vagas_precarias=4,
            vagas_precarias_restantes=4,
            vagas_definitivas=3,
            vagas_definitivas_restantes=3,
            status="1"
        )

        # Valor inicial
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

        # Cria escolha (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.PRECARIA,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

        # Verifica que a escolha foi criada
        assert escolha is not None

        # Verifica que a vaga foi decrementada
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial - 1
        # Verifica que vagas definitivas não foram alteradas
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

    def test_signal_nao_decrementa_se_situacao_nao_for_escolha(self):
        """Testa que o signal não decrementa vagas se a situação não for 'escolha'."""
        # Setup
        dre = Dre.objects.create(codigo="03", nome="DRE 03", sigla="DRE-03")
        escola = Escola.objects.create(
            codigo_eol="000003",
            nome_oficial="Escola Teste 3",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 3"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=102,
            cargo_descricao="Cargo Teste 3",
            vagas_precarias=2,
            vagas_precarias_restantes=2,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

        # Cria escolha com situação 'nao-escolha' (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

        # Verifica que a escolha foi criada
        assert escolha is not None

        # Verifica que as vagas NÃO foram decrementadas
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial

    def test_signal_nao_decrementa_se_vaga_escola_uuid_nao_fornecido(self):
        """Testa que o signal não decrementa se vaga_escola_uuid não for fornecido."""
        # Setup
        dre = Dre.objects.create(codigo="04", nome="DRE 04", sigla="DRE-04")
        escola = Escola.objects.create(
            codigo_eol="000004",
            nome_oficial="Escola Teste 4",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 4"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=103,
            cargo_descricao="Cargo Teste 4",
            vagas_precarias=2,
            vagas_precarias_restantes=2,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

        # Cria escolha sem vaga_escola_uuid (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=None,
        )

        # Verifica que a escolha foi criada
        assert escolha is not None

        # Verifica que as vagas NÃO foram decrementadas
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial

    def test_signal_nao_decrementa_se_tipo_vaga_nao_fornecido(self):
        """Testa que o signal não decrementa se tipo_vaga não for fornecido."""
        # Setup
        dre = Dre.objects.create(codigo="05", nome="DRE 05", sigla="DRE-05")
        escola = Escola.objects.create(
            codigo_eol="000005",
            nome_oficial="Escola Teste 5",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 5"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=104,
            cargo_descricao="Cargo Teste 5",
            vagas_precarias=2,
            vagas_precarias_restantes=2,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
        vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

        # Cria escolha sem tipo_vaga (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=None,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

        # Verifica que a escolha foi criada
        assert escolha is not None

        # Verifica que as vagas NÃO foram decrementadas
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
        assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial

    def test_signal_nao_falha_se_vaga_escola_nao_existir(self):
        """Testa que o signal não falha se a vaga_escola não existir."""
        # Cria escolha com vaga_escola_uuid inexistente (isso dispara o signal)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=uuid.uuid4(),  # UUID que não existe
        )

        # Verifica que a escolha foi criada mesmo com vaga inexistente
        assert escolha is not None
        assert Escolha.objects.filter(uuid=escolha.uuid).exists()

    def test_signal_decrementa_multiplas_escolhas_sequencialmente(self):
        """Testa que o signal decrementa corretamente múltiplas escolhas sequenciais."""
        # Setup
        dre = Dre.objects.create(codigo="06", nome="DRE 06", sigla="DRE-06")
        escola = Escola.objects.create(
            codigo_eol="000006",
            nome_oficial="Escola Teste 6",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 6"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=105,
            cargo_descricao="Cargo Teste 6",
            vagas_precarias=0,
            vagas_precarias_restantes=0,
            vagas_definitivas=3,
            vagas_definitivas_restantes=3,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

        # Cria 3 escolhas sequenciais
        for i in range(3):
            escolha = Escolha.objects.create(
                candidato_uuid=uuid.uuid4(),
                concurso_uuid=uuid.uuid4(),
                situacao=SituacaoChoices.ESCOLHA,
                tipo_vaga=TipoVagaChoices.DEFINITIVA,
                e_retardatario=False,
                vaga_escola_uuid=vaga_escola.uuid,
            )
            assert escolha is not None

        # Verifica que todas as vagas foram decrementadas
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial - 3
        assert vaga_escola.vagas_definitivas_restantes == 0

    def test_signal_nao_decrementa_em_atualizacao_apenas_em_criacao(self):
        """Testa que o signal só decrementa na criação, não na atualização."""
        # Setup
        dre = Dre.objects.create(codigo="07", nome="DRE 07", sigla="DRE-07")
        escola = Escola.objects.create(
            codigo_eol="000007",
            nome_oficial="Escola Teste 7",
            dre=dre,
            cep="04001-000"
        )
        lote = VagasEscolasLote.objects.create(
            processo_uuid=uuid.uuid4(),
            processo_nome="Processo Teste 7"
        )
        vaga_escola = VagasEscolas.objects.create(
            escola=escola,
            lote=lote,
            data_fechamento_modulo="2025-01-01",
            cargo_codigo=106,
            cargo_descricao="Cargo Teste 7",
            vagas_precarias=0,
            vagas_precarias_restantes=0,
            vagas_definitivas=5,
            vagas_definitivas_restantes=5,
            status="1"
        )

        # Valor inicial
        vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

        # Cria escolha (deve decrementar)
        escolha = Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.NAO_ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

        # Verifica que NÃO decrementou (porque situação não é 'escolha')
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

        # Atualiza a escolha para 'escolha' (não deve decrementar porque é atualização)
        escolha.situacao = SituacaoChoices.ESCOLHA
        escolha.save()

        # Verifica que ainda não decrementou (porque é atualização, não criação)
        vaga_escola.refresh_from_db()
        assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

