"""Módulo apps."""

from __future__ import annotations

from django.apps import AppConfig


class EscolhasConfig(AppConfig):
    """Representa EscolhasConfig."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "escolhas"

    def ready(self) -> None:
        """Importa os signals quando a aplicação estiver pronta."""
