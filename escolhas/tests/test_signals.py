import pytest
import uuid

from escolhas.models import Escolha, VagasEscolas, VagasEscolasLote, Escola, Dre
from escolhas.choices import SituacaoChoices, TipoVagaChoices


@pytest.fixture
def dre():
    """Fixture para criar uma DRE."""
    return Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")


@pytest.fixture
def escola(dre):
    """Fixture para criar uma escola."""
    return Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000"
    )


@pytest.fixture
def lote():
    """Fixture para criar um lote de vagas."""
    return VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(),
        processo_nome="Processo Teste"
    )


@pytest.fixture
def vaga_escola_com_vagas(escola, lote):
    """Fixture para criar uma vaga de escola com vagas definitivas e precárias."""
    return VagasEscolas.objects.create(
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


@pytest.mark.django_db
def test_signal_decrementa_vaga_definitiva_ao_criar_escolha(vaga_escola_com_vagas):
    """Testa se o signal decrementa vagas_definitivas_restantes ao criar uma escolha."""
    vagas_definitivas_inicial = vaga_escola_com_vagas.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola_uuid=vaga_escola_com_vagas.uuid,
    )

    vaga_escola_com_vagas.refresh_from_db()
    assert vaga_escola_com_vagas.vagas_definitivas_restantes == vagas_definitivas_inicial - 1
    assert vaga_escola_com_vagas.vagas_precarias_restantes == vagas_precarias_inicial

@pytest.mark.django_db
def test_signal_decrementa_vaga_precaria_ao_criar_escolha(escola, lote):
    """Testa se o signal decrementa vagas_precarias_restantes ao criar uma escolha."""
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

    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.PRECARIA,
        e_retardatario=False,
        vaga_escola_uuid=vaga_escola.uuid,
    )

    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial - 1
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

@pytest.mark.django_db
def test_signal_nao_decrementa_se_situacao_nao_for_escolha(escola, lote):
    """Testa que o signal não decrementa vagas se a situação não for 'escolha'."""
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

    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola_uuid=vaga_escola.uuid,
    )

    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial

@pytest.mark.django_db
def test_signal_nao_decrementa_se_vaga_escola_uuid_nao_fornecido(vaga_escola_com_vagas):
    """Testa que o signal não decrementa se vaga_escola_uuid não for fornecido."""
    vagas_definitivas_inicial = vaga_escola_com_vagas.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola_uuid=None,
    )

    vaga_escola_com_vagas.refresh_from_db()
    assert vaga_escola_com_vagas.vagas_definitivas_restantes == vagas_definitivas_inicial
    assert vaga_escola_com_vagas.vagas_precarias_restantes == vagas_precarias_inicial

@pytest.mark.django_db
def test_signal_nao_decrementa_se_tipo_vaga_nao_fornecido(vaga_escola_com_vagas):
    """Testa que o signal não decrementa se tipo_vaga não for fornecido."""
    vagas_definitivas_inicial = vaga_escola_com_vagas.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=None,
        e_retardatario=False,
        vaga_escola_uuid=vaga_escola_com_vagas.uuid,
    )

    vaga_escola_com_vagas.refresh_from_db()
    assert vaga_escola_com_vagas.vagas_definitivas_restantes == vagas_definitivas_inicial
    assert vaga_escola_com_vagas.vagas_precarias_restantes == vagas_precarias_inicial

@pytest.mark.django_db
def test_signal_nao_falha_se_vaga_escola_nao_existir():
    """Testa que o signal não falha se a vaga_escola não existir."""
    escolha = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola_uuid=uuid.uuid4(),
    )

    assert Escolha.objects.filter(uuid=escolha.uuid).exists()

@pytest.mark.django_db
def test_signal_decrementa_multiplas_escolhas_sequencialmente(escola, lote):
    """Testa que o signal decrementa corretamente múltiplas escolhas sequenciais."""
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

    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

    for _ in range(3):
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola_uuid=vaga_escola.uuid,
        )

    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial - 3
    assert vaga_escola.vagas_definitivas_restantes == 0

@pytest.mark.django_db
def test_signal_nao_decrementa_em_atualizacao_apenas_em_criacao(escola, lote):
    """Testa que o signal só decrementa na criação, não na atualização."""
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

    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes

    escolha = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola_uuid=vaga_escola.uuid,
    )

    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

    escolha.situacao = SituacaoChoices.ESCOLHA
    escolha.save()

    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial

