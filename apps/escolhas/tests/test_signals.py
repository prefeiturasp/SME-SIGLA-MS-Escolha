"""Módulo tests/test_signals."""

from __future__ import annotations

import uuid

import pytest

from escolhas.choices import SituacaoChoices, TipoVagaChoices
from escolhas.models import Escolha
from vagas_escolas.models import VagasEscolas


@pytest.fixture
def vaga_escola_com_vagas(escola, lote):
    """Fixture: vaga de escola com vagas definitivas e precárias."""
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
        status="1",
    )


@pytest.mark.django_db
def test_signal_decrementa_vaga_definitiva_ao_criar_escolha(
    vaga_escola_com_vagas,
):
    """Verifica signal decrementa vaga definitiva ao criar escolha."""
    vagas_definitivas_inicial = (
        vaga_escola_com_vagas.vagas_definitivas_restantes
    )
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes

    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola_com_vagas,
    )

    vaga_escola_com_vagas.refresh_from_db()
    assert (
        vaga_escola_com_vagas.vagas_definitivas_restantes
        == vagas_definitivas_inicial - 1
    )
    assert (
        vaga_escola_com_vagas.vagas_precarias_restantes
        == vagas_precarias_inicial
    )


@pytest.mark.django_db
def test_signal_decrementa_vaga_precaria_ao_criar_escolha(escola, lote):
    """Verifica signal decrementa vaga precaria ao criar escolha."""
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
        status="1",
    )
    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.PRECARIA,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial - 1
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial


@pytest.mark.django_db
def test_signal_nao_decrementa_se_situacao_nao_for_escolha(escola, lote):
    """Verifica signal nao decrementa se situacao nao for escolha."""
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
        status="1",
    )
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    vagas_precarias_inicial = vaga_escola.vagas_precarias_restantes
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
    assert vaga_escola.vagas_precarias_restantes == vagas_precarias_inicial


@pytest.mark.django_db
def test_signal_nao_decrementa_se_vaga_escola_nao_fornecido(
    vaga_escola_com_vagas,
):
    """Verifica signal nao decrementa se vaga escola nao fornecido."""
    vagas_definitivas_inicial = (
        vaga_escola_com_vagas.vagas_definitivas_restantes
    )
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=None,
    )
    vaga_escola_com_vagas.refresh_from_db()
    assert (
        vaga_escola_com_vagas.vagas_definitivas_restantes
        == vagas_definitivas_inicial
    )
    assert (
        vaga_escola_com_vagas.vagas_precarias_restantes
        == vagas_precarias_inicial
    )


@pytest.mark.django_db
def test_signal_nao_decrementa_se_tipo_vaga_nao_fornecido(
    vaga_escola_com_vagas,
):
    """Verifica signal nao decrementa se tipo vaga nao fornecido."""
    vagas_definitivas_inicial = (
        vaga_escola_com_vagas.vagas_definitivas_restantes
    )
    vagas_precarias_inicial = vaga_escola_com_vagas.vagas_precarias_restantes
    Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=None,
        e_retardatario=False,
        vaga_escola=vaga_escola_com_vagas,
    )
    vaga_escola_com_vagas.refresh_from_db()
    assert (
        vaga_escola_com_vagas.vagas_definitivas_restantes
        == vagas_definitivas_inicial
    )
    assert (
        vaga_escola_com_vagas.vagas_precarias_restantes
        == vagas_precarias_inicial
    )


@pytest.mark.django_db
def test_signal_nao_falha_se_vaga_escola_nao_existir():
    """Verifica signal nao falha se vaga escola nao existir."""
    escolha = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=None,
    )
    assert Escolha.objects.filter(uuid=escolha.uuid).exists()


@pytest.mark.django_db
def test_signal_decrementa_multiplas_escolhas_sequencialmente(escola, lote):
    """Verifica signal decrementa multiplas escolhas sequencialmente."""
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
        status="1",
    )
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    for _ in range(3):
        Escolha.objects.create(
            candidato_uuid=uuid.uuid4(),
            concurso_uuid=uuid.uuid4(),
            situacao=SituacaoChoices.ESCOLHA,
            tipo_vaga=TipoVagaChoices.DEFINITIVA,
            e_retardatario=False,
            vaga_escola=vaga_escola,
        )
    vaga_escola.refresh_from_db()
    assert (
        vaga_escola.vagas_definitivas_restantes
        == vagas_definitivas_inicial - 3
    )
    assert vaga_escola.vagas_definitivas_restantes == 0


@pytest.mark.django_db
def test_signal_nao_decrementa_em_atualizacao_apenas_em_criacao(escola, lote):
    """Verifica signal nao decrementa em atualizacao apenas em criacao."""
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
        status="1",
    )
    vagas_definitivas_inicial = vaga_escola.vagas_definitivas_restantes
    escolha = Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.NAO_ESCOLHA,
        tipo_vaga=TipoVagaChoices.DEFINITIVA,
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
    escolha.situacao = SituacaoChoices.ESCOLHA
    escolha.save()
    vaga_escola.refresh_from_db()
    assert vaga_escola.vagas_definitivas_restantes == vagas_definitivas_inicial
