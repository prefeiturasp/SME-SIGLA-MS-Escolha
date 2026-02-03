from uuid import uuid4
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from escolhas.services.exceptions import TipoUEDesabilitadoException

from escolhas.models import Dre, Escola, VagasEscolas, VagasEscolasLote


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def dre():
    return Dre.objects.create(codigo="01", nome="DRE 01")


@pytest.fixture
def escola(dre):
    return Escola.objects.create(codigo_eol="000001", nome_oficial="Escola Teste", dre=dre, cep="04001-000")


@pytest.fixture
def lote():
    return VagasEscolasLote.objects.create(processo_uuid=uuid4(), processo_nome="Proc")


@pytest.fixture
def vagas(escola, lote):
    v1 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=100,
        cargo_descricao="Cargo 1",
        vagas_precarias=3,
        vagas_definitivas=2,
        status="1"
    )
    v2 = VagasEscolas.objects.create(
        escola=escola,
        lote=lote,
        data_fechamento_modulo="2025-01-01",
        cargo_codigo=101,
        cargo_descricao="Cargo 2",
        vagas_precarias=1,
        vagas_definitivas=4,
        status="1"
    )
    return v1, v2


def test_action_utilizadas_patch_sucesso(api_client, lote, vagas):
    url = reverse('vagas-escolas-utilizadas')
    v1, v2 = vagas
    payload = [
        {"uuid": str(v1.uuid), "foi_utilizada": True, "vagas_precarias_utilizadas": 2},
        {"uuid": str(v2.uuid), "foi_utilizada": True, "vagas_definitivas_utilizadas": 3},
    ]
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data.get('total') == 2


def test_action_utilizadas_patch_lote_inexistente(api_client):
    url = reverse('vagas-escolas-utilizadas')
    payload = []
    resp = api_client.patch(url, payload, format='json')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data.get('total') == 0


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
    assert list_resp.data['total_vagas'] == 5
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
    client.post(url, payload(p1, eol1="123456"), format='json')
    p2 = uuid4()
    client.post(url, payload(p2, eol1="789012"), format='json')

    resp = client.get(url, {'cargo_codigo': 123})
    assert resp.status_code == 200
    assert len(resp.data.get('vagas', [])) >= 2
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


def test_create_retorna_400_quando_tipo_ue_desabilitado(api_client):
    url = reverse('vagas-escolas-list')
    p_uuid = uuid4()
    body = {
        "processo_uuid": str(p_uuid),
        "processo_nome": "Proc",
        "vagas": [{
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor",
            "codigo_eol": "123456",
            "vagas_precarias": 0,
            "vagas_definitivas": 1,
            "status": "ativo",
        }]
    }
    with patch('escolhas.views.vagas_escolas.processar_criacao_vagas_lote',
               side_effect=TipoUEDesabilitadoException("Tipo UE bloqueado")):
        resp = api_client.post(url, body, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.data.get('code') == 'TIPO_UE_DESABILITADO'
    assert 'Tipo UE bloqueado' in resp.data.get('detail', '')


def test_create_retorna_500_quando_excecao_generica(api_client):
    url = reverse('vagas-escolas-list')
    p_uuid = uuid4()
    body = {
        "processo_uuid": str(p_uuid),
        "processo_nome": "Proc",
        "vagas": [{
            "data_fechamento_modulo": "2025-09-10",
            "cargo_codigo": 123,
            "cargo_descricao": "Professor",
            "codigo_eol": "123456",
            "vagas_precarias": 0,
            "vagas_definitivas": 1,
            "status": "ativo",
        }]
    }
    with patch('escolhas.views.vagas_escolas.processar_criacao_vagas_lote',
               side_effect=Exception("falha inesperada")):
        resp = api_client.post(url, body, format='json')
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.data.get('code') == 'ERRO_AO_CRIAR_VAGAS_EM_LOTE'
    assert 'falha inesperada' in resp.data.get('detail', '')
