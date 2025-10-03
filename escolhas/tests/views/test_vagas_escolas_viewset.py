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
    vagas = list_resp.data.get('vagas', [])
    assert len(vagas) == 1
    assert vagas[0]['lote_uuid'] == lote2_uuid
    # total_vagas do último lote com uma vaga cargo 123 (2+3)
    assert list_resp.data['total_vagas'] == 5
    # dres devem conter codigo/nome/uuid
    assert isinstance(list_resp.data['dres'], list)
    assert {'codigo', 'nome', 'uuid'} <= set(list_resp.data['dres'][0].keys())


def test_list_processo_inexistente_retorna_vazio(escola_1):
    client = APIClient()
    url = reverse('vagas-escolas-list')
    resp = client.get(url, {'processo_uuid': str(uuid4())})
    assert resp.status_code == 200
    assert resp.data.get('vagas') == []
    assert resp.data['total_vagas'] == 0
    assert resp.data['dres'] == []


def test_filter_cargo_codigo_sozinho(escola_1, escola_2):
    client = APIClient()
    url = reverse('vagas-escolas-list')
    p1 = uuid4()
    client.post(url, payload(p1, eol1="123456"), format='json')  # cargo 123
    p2 = uuid4()
    client.post(url, payload(p2, eol1="789012"), format='json')  # cargo 123 no payload base

    resp = client.get(url, {'cargo_codigo': 123})
    assert resp.status_code == 200
    assert len(resp.data.get('vagas', [])) >= 2
    # total_vagas >= soma de todas as vagas cargo 123
    assert resp.data['total_vagas'] >= 10


def test_filter_por_processo_uuid_e_cargo_codigo(escola_1, escola_2):
    client = APIClient()
    url = reverse('vagas-escolas-list')
    p_uuid = uuid4()
    client.post(url, payload(p_uuid, eol1="123456", eol2="789012"), format='json')
    client.post(url, payload(p_uuid, eol1="123456"), format='json')

    resp_123 = client.get(url, {'processo_uuid': str(p_uuid), 'cargo_codigo': 123})
    assert resp_123.status_code == 200
    vagas_123 = resp_123.data.get('vagas', [])
    assert len(vagas_123) == 1
    assert vagas_123[0]['cargo_codigo'] == 123
    assert resp_123.data['total_vagas'] == 5

    resp_456 = client.get(url, {'processo_uuid': str(p_uuid), 'cargo_codigo': 456})
    assert resp_456.status_code == 200
    vagas_456 = resp_456.data.get('vagas', [])
    assert len(vagas_456) == 0
    assert resp_456.data['total_vagas'] == 0
