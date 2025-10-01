import pytest
from uuid import uuid4
from rest_framework.test import APIClient
from django.urls import reverse

from escolhas.models import VagasEscolas


pytestmark = pytest.mark.django_db


def payload(processo_uuid, eol1="123456", eol2=None):
    vagas = [
        {
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor de Matemática",
            "codigo_eol": eol1,
            "vagas_precarias": 2,
            "vagas_definitivas": 3,
            "status": "ativo",
        }
    ]
    if eol2:
        vagas.append({
            "data_fechamento_modulo": "2025-09-15",
            "cargo_codigo": 456,
            "cargo_descricao": "Professor de Português",
            "codigo_eol": eol2,
            "vagas_precarias": 1,
            "vagas_definitivas": 2,
            "status": "ativo",
        })
    return {
        "processo_uuid": str(processo_uuid),
        "processo_nome": "Processo Teste",
        "vagas": vagas,
    }


def test_post_cria_lote_e_vagas_e_list_retorna_so_ultimo_lote(escola_1, escola_2):
    p_uuid = uuid4()

    client = APIClient()
    url = reverse('vagas-escolas-list')

    resp1 = client.post(url, payload(p_uuid, eol1="123456", eol2="789012"), format='json')
    assert resp1.status_code in (201, 207)
    lote1_uuid = resp1.data['lote_uuid']
    assert VagasEscolas.objects.filter(lote__uuid=lote1_uuid).count() == 2

    resp2 = client.post(url, payload(p_uuid, eol1="123456"), format='json')
    assert resp2.status_code in (201, 207)
    lote2_uuid = resp2.data['lote_uuid']
    assert lote2_uuid != lote1_uuid
    assert VagasEscolas.objects.filter(lote__uuid=lote2_uuid).count() == 1

    list_resp = client.get(url, {'processo_uuid': str(p_uuid)})
    assert list_resp.status_code == 200
    results = list_resp.data.get('results', list_resp.data)
    assert len(results) == 1
    assert results[0]['lote_uuid'] == lote2_uuid


def test_list_processo_inexistente_retorna_vazio(escola_1):
    client = APIClient()
    url = reverse('vagas-escolas-list')
    resp = client.get(url, {'processo_uuid': str(uuid4())})
    assert resp.status_code == 200
    results = resp.data.get('results', resp.data)
    assert len(results) == 0
