"""Módulo tests/models/test_parametrizacao."""

from __future__ import annotations

import pytest

from escolhas.models import Dre, Escola, Parametrizacao


@pytest.mark.django_db
def test_parametrizacao_str_true_and_false() -> None:
    """Verifica parametrizacao str true and false."""
    p_true = Parametrizacao.objects.create(tipo_ue="EMEF", usar=True)
    p_false = Parametrizacao.objects.create(tipo_ue="EMEI", usar=False)
    assert str(p_true) == "EMEF (usar)"
    assert str(p_false) == "EMEI (não usar)"


def _criar_escola(
    dre: Dre, codigo_eol: str, nome: str, tipo_ue: str
) -> Escola:
    """Criar escola."""
    return Escola.objects.create(
        dre=dre,
        codigo_eol=codigo_eol,
        nome_oficial=nome,
        nome_nao_oficial=nome,
        tipo_unidade_admin="UNIDADE",
        tipo_ue=tipo_ue,
        logradouro="Rua A",
        numero="100",
        bairro="Centro",
        cep="01000-000",
        distrito="Distrito",
        sub_prefeitura="Sub",
        nome_dre=dre.nome,
        status="ATIVA",
    )


@pytest.mark.django_db
def test_sync_from_escolas_cria_parametrizacoes_que_faltam() -> None:
    """Verifica sync from escolas cria parametrizacoes que faltam."""
    dre = Dre.objects.create(codigo="01", nome="DRE 01", sigla="DRE-01")
    _criar_escola(dre, "100001", "Escola 1", "EMEF")
    _criar_escola(dre, "100002", "Escola 2", "EMEI")
    created = Parametrizacao.sync_from_escolas()
    assert created == 2
    tipos = set(Parametrizacao.objects.values_list("tipo_ue", flat=True))
    assert tipos == {"EMEF", "EMEI"}
    created_again = Parametrizacao.sync_from_escolas()
    assert created_again == 0
    assert Parametrizacao.objects.count() == 2


@pytest.mark.django_db
def test_sync_from_escolas_ignora_vazios_e_respeita_existentes() -> None:
    """Verifica sync from escolas ignora vazios e respeita existentes."""
    dre = Dre.objects.create(codigo="02", nome="DRE 02", sigla="DRE-02")
    Parametrizacao.objects.create(tipo_ue="EMEF", usar=False)
    _criar_escola(dre, "200001", "Escola A", "EMEF")
    _criar_escola(dre, "200002", "Escola B", "EMEI")
    _criar_escola(dre, "200003", "Escola C", "")
    created = Parametrizacao.sync_from_escolas()
    assert created == 1
    tipos = set(Parametrizacao.objects.values_list("tipo_ue", flat=True))
    assert tipos == {"EMEF", "EMEI"}
