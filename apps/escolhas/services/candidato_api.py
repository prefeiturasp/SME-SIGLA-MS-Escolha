"""Módulo services/candidato_api."""

from __future__ import annotations

import logging

from django.conf import settings
from sigla_sdk.context import get_correlation_id
from sigla_sdk.http.api_client import http_client

logger = logging.getLogger(__name__)


class CandidatoAPIService:
    """Consulta candidatos habilitados no microserviço MS-Candidatos."""

    def __init__(
        self, base_url: str | None = None, timeout_seconds: int = 30
    ) -> None:
        """Configura URL base e timeout da API de candidatos.

        Args:
            base_url: URL base do serviço remoto.
            timeout_seconds: Tempo máximo de espera, em segundos.
        """
        if base_url is None:
            base_url = settings.CANDIDATOS_API_URL
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            settings.API_KEY_HEADER: settings.CANDIDATOS_API_KEY,
        }

    def buscar_candidatos_por_cpfs(
        self, cpfs: list[str], processo_uuid: str
    ) -> str | None:
        """Localiza habilitados por CPFs e processo no MS-Candidatos.

        Args:
            cpfs: Lista de CPFs dos candidatos.
            processo_uuid: UUID do processo de convocação.

        Returns:
            Dados dos candidatos encontrados, ou None em caso de erro.
        """
        url = f"{self.base_url}/api/v1/habilitados/buscar-por-cpfs/"
        payload = {"processo_uuid": str(processo_uuid), "cpfs": cpfs}
        logger.info(
            f"Buscando candidatos por CPFs | method=POST | "
            f"correlation_id={get_correlation_id()} | url={url} | "
            f"processo_uuid={processo_uuid} | cpfs={cpfs}"
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
                f"Erro ao buscar candidatos por CPFs {cpfs} "
                f"no processo {processo_uuid}: {exc}",
                exc_info=True,
            )
            return None
        data = response.json()
        logger.info(
            f"Candidatos encontrados | correlation_id={get_correlation_id()} | "
            f"method=POST | url={url} | "
            f"processo_uuid={processo_uuid} | cpfs={cpfs}"
        )
        return data  # type: ignore[no-any-return]

    def buscar_habilitados_por_uuids(
        self,
        uuids: list[str],
        fields: list[str] | None = None,
    ) -> list[dict] | None:
        """Busca habilitados pelos códigos de identificação (UUIDs).

        Serve para, dada uma lista de identificadores (um por vínculo
        candidato–concurso), trazer as informações desses habilitados no
        serviço de candidatos — por exemplo só ``uuid`` e
        ``categoria_efetiva`` quando ``fields`` for informado.

        Args:
            uuids: Códigos de identificação dos habilitados a localizar.
            fields: Campos a retornar (query ``?fields=``). Ausente →
                resposta completa do habilitado.

        Returns:
            Lista com os habilitados encontrados. Se a lista de códigos
            estiver vazia, devolve lista vazia. Se a consulta falhar,
            devolve ``None``.
        """
        if not uuids:
            return []
        url = f"{self.base_url}/api/v1/habilitados/buscar-por-uuids/"
        payload = {"uuids": [str(item) for item in uuids]}
        params = {"fields": ",".join(fields)} if fields else None
        logger.info(
            f"Buscando habilitados por UUIDs | method=POST | "
            f"correlation_id={get_correlation_id()} | url={url} | "
            f"uuids={uuids} | fields={fields}"
        )
        try:
            response = http_client.post(
                url,
                json=payload,
                params=params,
                headers=self._default_headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            logger.error(
                f"Erro ao buscar habilitados por UUIDs {uuids}: {exc}",
                exc_info=True,
            )
            return None
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]  # type: ignore[no-any-return]
        if isinstance(data, list):
            return data
        return None

    def buscar_candidatos(
        self,
        nome: str | None = None,
        cpf: str | None = None,
        rg: str | None = None,
        registro_funcional: str | None = None,
    ) -> list[dict] | None:
        """Pesquisa candidatos por nome, CPF, RG ou registro funcional.

        Args:
            nome: Nome ou parte do nome do candidato.
            cpf: CPF do candidato.
            rg: RG do candidato.
            registro_funcional: Registro funcional do servidor.

        Returns:
            Lista de candidatos encontrados, ou None em caso de erro.
        """
        if not any(
            s and str(s).strip() for s in (nome, cpf, rg, registro_funcional)
        ):
            return []
        url = f"{self.base_url}/api/v1/candidatos/buscar/"
        logger.info(
            f"Buscando candidatos no MS-Candidatos | "
            f"correlation_id={get_correlation_id()} | url={url} | "
            f"nome={nome} | cpf={cpf} | rg={rg} | "
            f"registro_funcional={registro_funcional} | method=GET"
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
            logger.error(
                f"Erro ao buscar candidatos: {exc}",
                exc_info=True,
            )
            return None
        logger.info(
            f"Candidatos encontrados | "
            f"correlation_id={get_correlation_id()} | url={url} | "
            f"nome={nome} | cpf={cpf} | rg={rg} | "
            f"registro_funcional={registro_funcional} | method=GET | "
            f"status_code={response.status_code} | "
            f"response={str(response.json())[:100]}"
        )
        return response.json()  # type: ignore[no-any-return]
