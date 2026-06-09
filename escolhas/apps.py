"""Módulo apps."""
from __future__ import annotations
from typing import Any
from django.apps import AppConfig

class EscolhasConfig(AppConfig):
    """Define EscolhasConfig."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escolhas'

    def ready(self) -> None:
        """Importa os signals quando a aplicação estiver pronta."""
        import escolhas.signals
