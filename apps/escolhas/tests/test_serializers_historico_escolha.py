"""Testes unitários para HistoricoEscolhaSerializer.

(feature/143715-consulta-concursado).
"""

from __future__ import annotations

import uuid

import pytest

from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha, HistoricoEscolha
from escolhas.serializers.escolha import HistoricoEscolhaSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def escolha(vaga_escola):
    """Escolha."""
    return Escolha.objects.create(
        candidato_uuid=uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        situacao=SituacaoChoices.ESCOLHA,
        tipo_vaga="definitiva",
        e_retardatario=False,
        vaga_escola=vaga_escola,
    )


def test_historico_escolha_serializer_campos(escolha):
    """Verifica historico escolha serializer campos."""
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
    """Verifica historico escolha serializer situacao anterior null."""
    historico = HistoricoEscolha.objects.create(
        escolha=escolha,
        situacao_anterior=None,
        situacao_nova=SituacaoChoices.ESCOLHA,
    )
    serializer = HistoricoEscolhaSerializer(historico)
    assert serializer.data["situacao_anterior"] is None
    assert serializer.data["situacao_nova"] == SituacaoChoices.ESCOLHA


def test_historico_escolha_serializer_multiplos(escolha):
    """Verifica historico escolha serializer multiplos."""
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
    assert len(serializer.data) >= 2
    situacoes_novas = [item["situacao_nova"] for item in serializer.data]
    assert SituacaoChoices.RECONVOCACAO in situacoes_novas
    assert SituacaoChoices.ESCOLHA in situacoes_novas
