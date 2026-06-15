"""Módulo services/concurso_api."""

import logging
from typing import Any

from django.conf import settings
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


def _cargos_list_from_response(data: Any) -> list[dict]:
    """Extrai lista de cargos da resposta da API (lista direta ou paginada)."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "results" in data:
        return data["results"]  # type: ignore[no-any-return]
    return []


class ConcursoAPIService:
    """Consulta cargos e concursos no microserviço MS-Concursos."""

    @staticmethod
    def get_cargos_por_codigos(codigos: list[str]) -> dict[str, str]:
        """Busca nomes de cargos no MS-Concursos pelos códigos informados."""
        if not codigos:
            return {}
        base_url = getattr(settings, "CONCURSOS_API_URL", "").rstrip("/")
        if not base_url:
            logger.warning(
                "CONCURSOS_API_URL não configurado; "
                "não é possível obter nomes dos cargos."
            )
            return {}
        codigos_set = set(str(c) for c in codigos)
        result = {}
        url = f"{base_url}/api/v1/cargos/"
        logger.info(
            "Buscando cargos",
            extra={
                "correlation_id": get_correlation_id(),
                "method": "GET",
                "url": url,
                "codigos_set": codigos_set,
            },
        )
        try:
            for cod in codigos_set:
                response = http_client.get(
                    url, params={"codigo": cod}, timeout=30
                )
                response.raise_for_status()
                data = response.json()
                lista = _cargos_list_from_response(data)
                for item in lista:
                    if str(item.get("codigo")) == cod:
                        result[cod] = item.get("nome") or ""
                        break
            return result
        except Exception as exc:
            logger.warning(
                "Erro ao buscar cargos no MS-Concursos: %s",
                exc,
                exc_info=True,
            )
            return {}

    @staticmethod
    def buscar_concurso_uuid(concurso_uuid: str) -> str | None:
        """Consulta o MS-Concursos e devolve o UUID do concurso.

        Args:
            concurso_uuid: UUID do concurso relacionado.

        Returns:
            UUID confirmado pelo serviço, ou None se a consulta falhar.
        """
        try:
            base_url = settings.CONCURSOS_API_URL
            url = f"{base_url}/api/v1/concursos/{concurso_uuid}/"
            response = http_client.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get("uuid")  # type: ignore[no-any-return]

        except Exception as exc:
            logger.error(
                f"Erro ao buscar concurso_uuid para concurso "
                f"{concurso_uuid}: {exc}",
                exc_info=True,
            )
            return None
