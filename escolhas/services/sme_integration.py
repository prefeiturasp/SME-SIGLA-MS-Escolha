from typing import Any

import requests
from django.conf import settings


def _get_base_url_and_headers() -> tuple[str, dict[str, str]]:
    base_url = getattr(settings, "SMEINTEGRACAO_API_URL", None)
    token = getattr(settings, "SMEINTEGRACAO_API_TOKEN", None)

    if not base_url:
        raise ValueError("SMEINTEGRACAO_API_URL não configurada")
    if not token:
        raise ValueError("SMEINTEGRACAO_API_TOKEN não configurada")

    headers = {
        "x-api-eol-key": token,
        "Accept": "application/json",
    }
    return base_url.rstrip("/"), headers


def buscar_dres_de_smeintegracao() -> list[dict[str, Any]]:
    base_url, headers = _get_base_url_and_headers()
    url = base_url + "/api/DREs"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("Formato de resposta inesperado ao buscar DREs")

    list_dres: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        codigo = item.get("codigoDRE")
        nome = item.get("nomeDRE")
        sigla = item.get("siglaDRE")
        if not codigo or not nome or not sigla:
            continue
        list_dres.append(
            {
                "codigo": str(codigo),
                "nome": str(nome),
                "sigla": str(sigla),
            }
        )

    return list_dres


def buscar_ues_codigos_por_dre(codigo_dre: str) -> list[str]:
    base_url, headers = _get_base_url_and_headers()
    url = base_url + f"/api/DREs/{codigo_dre}/ues"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(
            "Formato de resposta inesperado ao buscar UEs por DRE"
        )

    return [str(code) for code in payload if code is not None]


def buscar_dados_escola_por_eol(codigo_eol: str) -> dict[str, Any]:
    base_url, headers = _get_base_url_and_headers()
    url = base_url + f"/api/escolas/dados/{codigo_eol}"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(
            "Formato de resposta inesperado ao buscar dados da escola"
        )

    return payload


def buscar_unidades_codigo_integracao_por_dre(
    codigo_dre: str,
) -> list[dict[str, Any]]:
    """
    GET /api/DREs/{dreCodigo}/unidades/codigo-integracao
    Retorna lista com codigoUe, nomeUe, codigoIntegracao.
    """
    base_url, headers = _get_base_url_and_headers()
    url = base_url + f"/api/DREs/{codigo_dre}/unidades/codigo-integracao"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    result = response.json()
    if not isinstance(result, list):
        raise ValueError(
            "Formato de resposta inesperado ao buscar unidades/codigo-integracao"  # noqa: E501
        )

    return result
