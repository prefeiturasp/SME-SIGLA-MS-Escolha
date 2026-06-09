"""Módulo apps."""
from __future__ import annotations
from typing import Any
from django.apps import AppConfig

class EscolhasConfig(AppConfig):
    """Define EscolhasConfig."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escolhas'

    def ready(self) -> None:
        """Importa os signals quando a aplicação estiver pronta.
        
        Args:
            self: Instância do objeto.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        import escolhas.signals
