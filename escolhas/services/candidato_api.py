from typing import Optional
import logging
import requests
from django.conf import settings
from typing import List

logger = logging.getLogger(__name__)


class CandidatoAPIService:
    """Service para integração com MS-Candidatos."""

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: int = 30):
        """
        Inicializa o serviço de candidatos.

        Args:
            base_url: URL base da API de candidatos. Se não fornecido, usa CANDIDATOS_API_URL do settings.
            timeout_seconds: Timeout em segundos para as requisições
        """
        if base_url is None:
            base_url = settings.CANDIDATOS_API_URL
        
        self.base_url = base_url.rstrip('/')
        self.timeout_seconds = timeout_seconds
        self._default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def buscar_candidatos_por_cpfs(self, cpfs: List[str], processo_uuid: str) -> Optional[str]:
        """
        Busca candidatos por CPFs.
        
        Args:
            cpfs: List[str] de CPFs dos candidatos
            processo_uuid: UUID do processo de convocação
        Returns:
            List[Dict[str, Any]] de candidatos encontrados
        """
        try:
            url = f"{self.base_url}/api/v1/habilitados/buscar-por-cpfs/"
            payload = {
                'processo_uuid': str(processo_uuid),
                'cpfs': cpfs,
            }
            
            logger.info(f'Buscando candidatos por CPFs {cpfs} no processo {processo_uuid}')
            response = requests.post(
                url,
                json=payload,
                headers=self._default_headers,
                timeout=self.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()

            return data
        
        except requests.exceptions.RequestException as exc:
            logger.error(f'Erro HTTP ao buscar candidatos por CPFs {cpfs} no processo {processo_uuid}: {exc}')
            return None
        except Exception as exc:
            logger.error(f'Erro ao buscar candidatos por CPFs {cpfs} no processo {processo_uuid}: {exc}', exc_info=True)
            return None

    def buscar_candidatos(
        self,
        nome: Optional[str] = None,
        cpf: Optional[str] = None,
        rg: Optional[str] = None,
        registro_funcional: Optional[str] = None,
    ) -> Optional[List[dict]]:
        """
        Busca candidatos no MS-Candidatos por nome, CPF, RG ou registro funcional.
        Pelo menos um dos parâmetros deve ser informado.

        Args:
            nome: Nome (busca por contém).
            cpf: CPF (busca por contém).
            rg: RG (busca por contém).
            registro_funcional: Registro funcional (busca por contém).

        Returns:
            Lista de candidatos retornados pela API ou None em caso de erro.
        """
        if not any(s and str(s).strip() for s in (nome, cpf, rg, registro_funcional)):
            return []

        try:
            url = f"{self.base_url}/api/v1/candidatos/buscar/"
            params = {}
            if nome and str(nome).strip():
                params['nome'] = str(nome).strip()
            if cpf and str(cpf).strip():
                params['cpf'] = str(cpf).strip()
            if rg and str(rg).strip():
                params['rg'] = str(rg).strip()
            if registro_funcional and str(registro_funcional).strip():
                params['registro_funcional'] = str(registro_funcional).strip()

            response = requests.get(
                url,
                params=params,
                headers=self._default_headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error('Erro HTTP ao buscar candidatos: %s', exc)
            return None
        except Exception as exc:
            logger.error('Erro ao buscar candidatos: %s', exc, exc_info=True)
            return None
