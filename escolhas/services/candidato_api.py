"""Módulo services/candidato_api."""

from __future__ import annotations

import logging

from django.conf import settings
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class CandidatoAPIService:
    """Service para integração com MS-Candidatos."""

    def __init__(
        self, base_url: str | None = None, timeout_seconds: int = 30
    ) -> None:
        """Inicializa a instância com os parâmetros informados.

        Args:
            self: Instância do objeto.
            base_url: URL base do serviço remoto.
            timeout_seconds: Tempo máximo de espera pela resposta, em segundos.
        """
        if base_url is None:
            base_url = settings.CANDIDATOS_API_URL
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def buscar_candidatos_por_cpfs(
        self, cpfs: list[str], processo_uuid: str
    ) -> str | None:
        """Busca candidatos por cpfs.

        Args:
            self: Instância do objeto.
            cpfs: Cpfs utilizado na operação.
            processo_uuid: UUID do processo de convocação.

        Returns:
            Texto resultante da operação.
        """
        url = f"{self.base_url}/api/v1/habilitados/buscar-por-cpfs/"
        payload = {"processo_uuid": str(processo_uuid), "cpfs": cpfs}
        logger.info(
            "Buscando candidatos por CPFs",
            extra={
                "method": "POST",
                "correlation_id": get_correlation_id(),
                "url": url,
                "processo_uuid": processo_uuid,
                "cpfs": cpfs,
                "headers": self._default_headers,
            },
        )
        try:
            response = http_client.post(
                url,
                json=payload,
                headers=self._default_headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.error(
                "Erro ao buscar candidatos por CPFs %s no processo %s: %s",
                cpfs,
                processo_uuid,
                exc,
                exc_info=True,
            )
            return None
        data = response.json()
        logger.info(
            "Candidatos encontrados",
            extra={
                "correlation_id": get_correlation_id(),
                "method": "POST",
                "url": url,
                "processo_uuid": processo_uuid,
                "cpfs": cpfs,
            },
        )
        return data  # type: ignore[no-any-return]

    def buscar_candidatos(
        self,
        nome: str | None = None,
        cpf: str | None = None,
        rg: str | None = None,
        registro_funcional: str | None = None,
    ) -> list[dict] | None:
        """Busca candidatos.

        Args:
            self: Instância do objeto.
            nome: Nome utilizado na operação.
            cpf: Cpf utilizado na operação.
            rg: Rg utilizado na operação.
            registro_funcional: Registro funcional utilizado na operação.

        Returns:
            Lista com os registros obtidos.
        """
        if not any(
            s and str(s).strip() for s in (nome, cpf, rg, registro_funcional)
        ):
            return []
        url = f"{self.base_url}/api/v1/candidatos/buscar/"
        logger.info(
            "Buscando candidatos no MS-Candidatos",
            extra={
                "correlation_id": get_correlation_id(),
                "url": url,
                "nome": nome,
                "cpf": cpf,
                "rg": rg,
                "registro_funcional": registro_funcional,
                "method": "GET",
                "headers": self._default_headers,
            },
        )
        params = {}
        if nome and str(nome).strip():
            params["nome"] = str(nome).strip()
        if cpf and str(cpf).strip():
            params["cpf"] = str(cpf).strip()
        if rg and str(rg).strip():
            params["rg"] = str(rg).strip()
        if registro_funcional and str(registro_funcional).strip():
            params["registro_funcional"] = str(registro_funcional).strip()
        try:
            response = http_client.get(
                url,
                params=params,
                headers=self._default_headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.error("Erro ao buscar candidatos: %s", exc, exc_info=True)
            return None
        logger.info(
            "Candidatos encontrados",
            extra={
                "correlation_id": get_correlation_id(),
                "url": url,
                "nome": nome,
                "cpf": cpf,
                "rg": rg,
                "registro_funcional": registro_funcional,
                "method": "GET",
                "headers": self._default_headers,
                "status_code": response.status_code,
                "response": str(response.json())[:100],
            },
        )
        return response.json()  # type: ignore[no-any-return]
