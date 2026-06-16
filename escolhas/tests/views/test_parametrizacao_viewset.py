"""Módulo tests/views/test_parametrizacao_viewset."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status

from escolhas.models import Parametrizacao

MAPPING_FIXTURE = [
    ("CCA", "cca"),
    ("CCI/CIPS", "ccicips"),
    ("CECI", "ceci"),
    ("CEI DIRET", "cei-diret"),
    ("CEI INDIR", "cei-indir"),
    ("CEMEI", "cemei"),
    ("CEU AT COMPL", "ceu-at-compl"),
    ("CEU CEI", "ceu-cei"),
    ("CEU CEMEI", "ceu-cemei"),
    ("CEU EMEF", "ceu-emef"),
    ("CEU EMEI", "ceu-emei"),
    ("CEU POLO", "ceu-polo"),
    ("CIEJA", "cieja"),
    ("CMCT", "cmct"),
    ("CR.P.CONV", "crpconv"),
    ("EMEBS", "emebs"),
    ("EMEF", "emef"),
    ("EMEFM", "emefm"),
    ("EMEF P FOM", "emef-p-fom"),
    ("EMEI", "emei"),
    ("EMEI P FOM", "emei-p-fom"),
    ("ESC.PART.", "escpart"),
    ("ESP CONV", "esp-conv"),
    ("E TEC", "e-tec"),
    ("MOVA", "mova"),
]


@pytest.fixture
def parametrizacoes_db():
    """Parametrizacoes db."""
    objs = [
        Parametrizacao(tipo_ue=nome, usar=False)
        for nome, slug in MAPPING_FIXTURE
    ]
    Parametrizacao.objects.bulk_create(objs)
    return list(Parametrizacao.objects.all())


@pytest.mark.django_db
def test_list_parametrizacoes(api_client, parametrizacoes_db):
    """Verifica list parametrizacoes."""
    url = reverse("parametrizacao-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    items = response.data
    assert isinstance(items, list)
    assert len(items) == len(MAPPING_FIXTURE)


@pytest.mark.django_db
def test_bulk_update_usar_updates_multiple(api_client, parametrizacoes_db):
    """Verifica bulk update usar updates multiple."""
    p1 = Parametrizacao.objects.get(tipo_ue="EMEF")
    p2 = Parametrizacao.objects.get(tipo_ue="EMEI")
    assert p1.usar is False and p2.usar is False
    url = reverse("parametrizacao-bulk")
    payload = [
        {"uuid": str(p1.uuid), "usar": True},
        {"uuid": str(p2.uuid), "usar": True},
    ]
    resp = api_client.patch(url, payload, format="json")
    assert resp.status_code == status.HTTP_200_OK
    assert "updated" in resp.data and resp.data["updated"] == 2
    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.usar is True
    assert p2.usar is True
