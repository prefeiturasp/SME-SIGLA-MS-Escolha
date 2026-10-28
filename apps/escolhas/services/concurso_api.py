"""Módulo services/concurso_api."""

import logging
from typing import Any

from django.conf import settings
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

from escolhas.services.http_log import mascarar_headers

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

    TIMEOUT_SECONDS = 30

    def __init__(self) -> None:
        """Inicializa URL base, headers e timeout do MS-Concursos."""
        self.base_url = (
            getattr(settings, "CONCURSOS_API_URL", "") or ""
        ).rstrip("/")
        self.timeout_seconds = self.TIMEOUT_SECONDS
        self.headers: dict[str, str] = {
            "Accept": "application/json",
            settings.API_KEY_HEADER: settings.CONCURSOS_API_KEY,
        }

    def get_cargos_por_codigos(self, codigos: list[str]) -> dict[str, str]:
        """Busca nomes de cargos no MS-Concursos pelos códigos informados."""
        if not codigos:
            return {}
        if not self.base_url:
            logger.warning(
                "CONCURSOS_API_URL não configurado; "
                "não é possível obter nomes dos cargos. | "
                f"headers={mascarar_headers(self.headers)} | "
                f"timeout_seconds={self.timeout_seconds}"
            )
            return {}
        codigos_set = set(str(c) for c in codigos)
        result = {}
        url = f"{self.base_url}/api/v1/cargos/"
        logger.info(
            f"Buscando cargos | correlation_id={get_correlation_id()} | "
            f"method=GET | url={url} | codigos_set={codigos_set} | "
            f"headers={mascarar_headers(self.headers)} | "
            f"timeout_seconds={self.timeout_seconds}"
        )
        try:
            for cod in codigos_set:
                response = http_client.get(
                    url,
                    params={"codigo": cod},
                    headers=self.headers,
                    timeout=self.timeout_seconds,
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
                f"Erro ao buscar cargos no MS-Concursos: {exc} | "
                f"correlation_id={get_correlation_id()} | url={url} | "
                f"codigos_set={codigos_set} | method=GET | ",
                exc_info=True,
            )
            return {}

    def buscar_concurso_uuid(self, concurso_uuid: str) -> str | None:
        """Consulta o MS-Concursos e devolve o UUID do concurso.

        Args:
            concurso_uuid: UUID do concurso relacionado.

        Returns:
            UUID confirmado pelo serviço, ou None se a consulta falhar.
        """
        url = f"{self.base_url}/api/v1/concursos/{concurso_uuid}/"
        logger.info(
            f"Buscando concurso_uuid para concurso {concurso_uuid} | "
            f"correlation_id={get_correlation_id()} | url={url} | "
            f"headers={mascarar_headers(self.headers)} | "
            f"timeout_seconds={self.timeout_seconds}"
        )
        try:
            response = http_client.get(
                url,
                headers=self.headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json().get("uuid")  # type: ignore[no-any-return]

        except Exception as exc:
            logger.error(
                f"Erro ao buscar concurso_uuid para concurso "
                f"{concurso_uuid}: {exc} | "
                f"correlation_id={get_correlation_id()} | url={url} | "
                 f"method=GET | ",
                exc_info=True,
            )
            return None
