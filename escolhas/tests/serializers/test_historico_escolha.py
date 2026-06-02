"""
Testes unitários para HistoricoEscolhaSerializer
(feature/143715-consulta-concursado).
"""

import uuid

import pytest

from escolhas.choices import SituacaoChoices
from escolhas.models import (
    Dre,
    Escola,
    Escolha,
    HistoricoEscolha,
    VagasEscolas,
    VagasEscolasLote,
)
from escolhas.serializers.escolha import HistoricoEscolhaSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre():
    return Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")


@pytest.fixture
def escola(dre):
    return Escola.objects.create(
        codigo_eol="000001",
        nome_oficial="Escola Teste",
        dre=dre,
        cep="04001-000",
    )


@pytest.fixture
def lote():
    return VagasEscolasLote.objects.create(
        processo_uuid=uuid.uuid4(),
        processo_nome="Processo Teste",
    )


@pytest.fixture
def vaga_escola(escola, lote):
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


@pytest.fixture
def escolha(vaga_escola):
    return Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga="definitiva",
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )


def test_historico_escolha_serializer_campos(escolha):
    """
    HistoricoEscolhaSerializer deve serializar uuid, situacao_anterior,
    situacao_nova, criado_em.
    """
    historico = HistoricoEscolha.objects.create(
        escolha=escolha,
        situacao_anterior=SituacaoChoices.NAO_ESCOLHA,
        situacao_nova=SituacaoChoices.ESCOLHA,
    )
    serializer = HistoricoEscolhaSerializer(historico)
    data = serializer.data
    assert "uuid" in data
    assert data["uuid"] == str(historico.uuid)
    assert data["situacao_anterior"] == SituacaoChoices.NAO_ESCOLHA
    assert data["situacao_nova"] == SituacaoChoices.ESCOLHA
    assert "criado_em" in data


def test_historico_escolha_serializer_situacao_anterior_null(escolha):
    """situacao_anterior pode ser null (primeira situação)."""
    historico = HistoricoEscolha.objects.create(
        escolha=escolha,
        situacao_anterior=None,
        situacao_nova=SituacaoChoices.ESCOLHA,
    )
    serializer = HistoricoEscolhaSerializer(historico)
    assert serializer.data["situacao_anterior"] is None
    assert serializer.data["situacao_nova"] == SituacaoChoices.ESCOLHA


def test_historico_escolha_serializer_multiplos(escolha):
    """
    Serializer com many=True deve retornar lista de históricos (inclui os
    criados pelo signal).
    """
    HistoricoEscolha.objects.create(
        escolha=escolha,
        situacao_anterior=None,
        situacao_nova=SituacaoChoices.ESCOLHA,
    )
    HistoricoEscolha.objects.create(
        escolha=escolha,
        situacao_anterior=SituacaoChoices.ESCOLHA,
        situacao_nova=SituacaoChoices.RECONVOCACAO,
    )
    qs = HistoricoEscolha.objects.filter(escolha=escolha).order_by(
        "-criado_em"
    )
    serializer = HistoricoEscolhaSerializer(qs, many=True)
    # Pode haver 1 histórico criado pelo signal ao criar a Escolha + os 2 que criamos  # noqa: E501
    assert len(serializer.data) >= 2
    situacoes_novas = [item["situacao_nova"] for item in serializer.data]
    assert SituacaoChoices.RECONVOCACAO in situacoes_novas
    assert SituacaoChoices.ESCOLHA in situacoes_novas
