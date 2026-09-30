"""Testes unitários do service de extração de dados."""

from __future__ import annotations

import uuid
from unittest.mock import Mock, patch

from escolhas.constants import SituacaoChoices
from escolhas.services import extracao_dados as service

REPO_BUSCAR = (
    "escolhas.services.extracao_dados."
    "EscolhaRepository.buscar_escolhas_por_escopo"
)
REPO_ULTIMA = (
    "escolhas.services.extracao_dados."
    "EscolhaRepository.obter_ultima_escolha_em"
)


def test_contar_escolhas_por_situacao_e_categoria():
    """Cruza situação com categoria efetiva do candidato."""
    geral = str(uuid.uuid4())
    nna = str(uuid.uuid4())
    sem_cat = str(uuid.uuid4())

    resultado = service.contar_escolhas_por_situacao_e_categoria(
        [
            {"candidato_uuid": geral, "situacao": SituacaoChoices.ESCOLHA},
            {"candidato_uuid": nna, "situacao": SituacaoChoices.ESCOLHA},
            {
                "candidato_uuid": sem_cat,
                "situacao": SituacaoChoices.NAO_ESCOLHA,
            },
            {
                "candidato_uuid": geral,
                "situacao": SituacaoChoices.RECONVOCACAO,
            },
        ],
        {geral: "GERAL", nna: "NNA"},
    )

    assert resultado["escolha"] == {
        "total": 2,
        "geral": 1,
        "pcd": 0,
        "nna": 1,
    }
    assert resultado["nao-escolha"] == {
        "total": 1,
        "geral": 0,
        "pcd": 0,
        "nna": 0,
    }
    assert resultado["reconvocacao"] == {
        "total": 1,
        "geral": 1,
        "pcd": 0,
        "nna": 0,
    }


def test_contar_escolhas_por_situacao_e_categoria_lista_vazia():
    """Sem escolhas, retorna blocos zerados."""
    resultado = service.contar_escolhas_por_situacao_e_categoria([], {})
    assert resultado["escolha"] == {
        "total": 0,
        "geral": 0,
        "pcd": 0,
        "nna": 0,
    }


def test_buscar_categorias_efetivas_lista_vazia():
    """Sem UUIDs, não chama a API."""
    assert service.buscar_categorias_efetivas([]) == {}


@patch("escolhas.services.extracao_dados.CandidatoAPIService")
def test_buscar_categorias_efetivas_sucesso(mock_api_cls):
    """Monta mapa uuid → categoria a partir do MS-Candidatos."""
    mock_api = Mock()
    mock_api.buscar_habilitados_por_uuids.return_value = [
        {"uuid": "a", "categoria_efetiva": "GERAL"},
        {"uuid": "b", "categoria_efetiva": "PCD"},
        {"uuid": "c", "categoria_efetiva": None},
        {"uuid": None, "categoria_efetiva": "NNA"},
    ]
    mock_api_cls.return_value = mock_api

    resultado = service.buscar_categorias_efetivas(["a", "b", "c"])

    assert resultado == {"a": "GERAL", "b": "PCD"}
    mock_api.buscar_habilitados_por_uuids.assert_called_once_with(
        ["a", "b", "c"],
        fields=["uuid", "categoria_efetiva"],
    )


@patch("escolhas.services.extracao_dados.CandidatoAPIService")
def test_buscar_categorias_efetivas_falha_api(mock_api_cls):
    """Falha na API retorna mapa vazio."""
    mock_api = Mock()
    mock_api.buscar_habilitados_por_uuids.return_value = None
    mock_api_cls.return_value = mock_api

    assert service.buscar_categorias_efetivas(["a"]) == {}


@patch("escolhas.services.extracao_dados.buscar_categorias_efetivas")
@patch(REPO_BUSCAR)
def test_contar_escolhas_orquestra_repo_e_categorias(
    mock_buscar, mock_categorias
):
    """Busca escolhas, consulta categorias e monta contagens."""
    cand = str(uuid.uuid4())
    mock_buscar.return_value = [
        {"candidato_uuid": cand, "situacao": SituacaoChoices.ESCOLHA}
    ]
    mock_categorias.return_value = {cand: "GERAL"}

    resultado = service.contar_escolhas(
        concurso_uuid="concurso",
        ano=2026,
        processo_uuids=["p1"],
    )

    mock_buscar.assert_called_once_with(
        concurso_uuid="concurso",
        ano=2026,
        processo_uuids=["p1"],
    )
    mock_categorias.assert_called_once_with([cand])
    assert resultado["escolha"]["total"] == 1
    assert resultado["escolha"]["geral"] == 1


@patch(REPO_ULTIMA)
@patch("escolhas.services.extracao_dados.montar_dres_concursos")
@patch("escolhas.services.extracao_dados.montar_dres")
@patch("escolhas.services.extracao_dados.contar_escolhas")
def test_montar_extracao_dados_com_filtros(
    mock_contar, mock_dres, mock_dres_concursos, mock_ultima
):
    """Com filtros, quebra a resposta por ano."""
    concurso = str(uuid.uuid4())
    processo = str(uuid.uuid4())
    mock_contar.return_value = {
        "escolha": {"total": 1, "geral": 1, "pcd": 0, "nna": 0},
        "nao-escolha": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
        "reconvocacao": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
    }
    mock_dres.return_value = []
    mock_dres_concursos.return_value = {}
    mock_ultima.return_value = None

    resultado = service.montar_extracao_dados(
        concurso_uuid=concurso,
        filtros=[{"ano": 2026, "processo_uuids": [processo]}],
    )

    assert resultado["concurso_uuid"] == concurso
    assert resultado["filtros"] == [
        {"ano": 2026, "processo_uuids": [processo]}
    ]
    assert resultado["2026"]["escolha"]["total"] == 1
    assert "dres" in resultado["2026"]
    assert "dres_concursos" in resultado
    assert "ultima_escolha_em" in resultado
    mock_contar.assert_called_once_with(
        concurso, 2026, processo_uuids=[processo]
    )


@patch(REPO_ULTIMA)
@patch("escolhas.services.extracao_dados.montar_dres_concursos")
@patch("escolhas.services.extracao_dados.montar_dres")
@patch("escolhas.services.extracao_dados.contar_escolhas")
def test_montar_extracao_dados_sem_filtros(
    mock_contar, mock_dres, mock_dres_concursos, mock_ultima
):
    """Sem filtros, agrega na raiz."""
    mock_contar.return_value = {
        "escolha": {"total": 2, "geral": 2, "pcd": 0, "nna": 0},
        "nao-escolha": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
        "reconvocacao": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
    }
    mock_dres.return_value = [{"nome": "DRE-A", "escolhas": 2, "vagas": 10}]
    mock_dres_concursos.return_value = {}
    mock_ultima.return_value = "2026-01-01T00:00:00+00:00"

    resultado = service.montar_extracao_dados(concurso_uuid=None, filtros=None)

    assert resultado["escolha"]["total"] == 2
    assert resultado["dres"][0]["nome"] == "DRE-A"
    assert resultado["ultima_escolha_em"] == "2026-01-01T00:00:00+00:00"
    assert "filtros" not in resultado
    mock_contar.assert_called_once_with(None, ano=None)
