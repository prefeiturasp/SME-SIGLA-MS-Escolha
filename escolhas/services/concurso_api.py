from typing import Optional
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ConcursoAPIService:
    """Service para integração com MS-ProcessosConvocacao."""

    @staticmethod
    def buscar_concurso_uuid(concurso_uuid: str) -> Optional[str]:
        """
        Busca concurso_uuid a partir do concurso_uuid via MS-ProcessosConvocacao.
        
        Args:
            concurso_uuid: UUID do concurso
            
        Returns:
            UUID do concurso se encontrado, None caso contrário
        """
        try:
            base_url = settings.CONCURSOS_API_URL
            url = f"{base_url}/api/v1/concursos/{concurso_uuid}/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get('uuid')
        
        except requests.exceptions.RequestException as exc:
            logger.error(f'Erro HTTP ao buscar concurso_uuid para concurso {concurso_uuid}: {exc}')
            return None
        except Exception as exc:
            logger.error(f'Erro ao buscar concurso_uuid para concurso {concurso_uuid}: {exc}', exc_info=True)
            return None

