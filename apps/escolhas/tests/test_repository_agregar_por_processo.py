"""Testes de EscolhaRepository.agregar_por_processo_e_situacao."""

from __future__ import annotations

import uuid

import pytest

from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha
from escolhas.repository import EscolhaRepository

pytestmark = pytest.mark.django_db


def _criar_escolha(*, processo_uuid, situacao, candidato_uuid=None):
    """Persiste uma escolha mínima para o teste."""
    return Escolha.objects.create(
        candidato_uuid=candidato_uuid or uuid.uuid4(),
        concurso_uuid=uuid.uuid4(),
        processo_uuid=processo_uuid,
        situacao=situacao,
    )


def test_agregar_lista_vazia_retorna_dict_vazio():
    """Sem processo_uuids, retorna dicionário vazio."""
    assert EscolhaRepository.agregar_por_processo_e_situacao([]) == {}


def test_agregar_inicializa_blocos_sem_registros():
    """Processo sem escolhas vem com totais zerados."""
    pid = str(uuid.uuid4())
    resultado = EscolhaRepository.agregar_por_processo_e_situacao([pid])

    assert set(resultado.keys()) == {pid}
    assert resultado[pid] == {
        "escolha": {"total": 0, "candidatos_uuids": []},
        "nao-escolha": {"total": 0, "candidatos_uuids": []},
        "reconvocacao": {"total": 0, "candidatos_uuids": []},
    }


def test_agregar_por_situacao_e_processo():
    """Agrupe UUIDs e totais por situação no processo."""
    processo = uuid.uuid4()
    outro = uuid.uuid4()
    cand_escolha = uuid.uuid4()
    cand_nao = uuid.uuid4()
    cand_recon = uuid.uuid4()

    _criar_escolha(
        processo_uuid=processo,
        situacao=SituacaoChoices.ESCOLHA,
        candidato_uuid=cand_escolha,
    )
    _criar_escolha(
        processo_uuid=processo,
        situacao=SituacaoChoices.NAO_ESCOLHA,
        candidato_uuid=cand_nao,
    )
    _criar_escolha(
        processo_uuid=processo,
        situacao=SituacaoChoices.RECONVOCACAO,
        candidato_uuid=cand_recon,
    )
    _criar_escolha(
        processo_uuid=outro,
        situacao=SituacaoChoices.ESCOLHA,
    )

    resultado = EscolhaRepository.agregar_por_processo_e_situacao(
        [str(processo)]
    )
    pid = str(processo)

    assert resultado[pid]["escolha"] == {
        "total": 1,
        "candidatos_uuids": [str(cand_escolha)],
    }
    assert resultado[pid]["nao-escolha"] == {
        "total": 1,
        "candidatos_uuids": [str(cand_nao)],
    }
    assert resultado[pid]["reconvocacao"] == {
        "total": 1,
        "candidatos_uuids": [str(cand_recon)],
    }
    assert str(outro) not in resultado


def test_agregar_ignora_candidato_uuid_nulo():
    """Escolhas sem candidato_uuid não entram na agregação."""
    processo = uuid.uuid4()
    Escolha.objects.create(
        candidato_uuid=None,
        concurso_uuid=uuid.uuid4(),
        processo_uuid=processo,
        situacao=SituacaoChoices.ESCOLHA,
    )

    resultado = EscolhaRepository.agregar_por_processo_e_situacao(
        [str(processo)]
    )

    assert resultado[str(processo)]["escolha"] == {
        "total": 0,
        "candidatos_uuids": [],
    }
