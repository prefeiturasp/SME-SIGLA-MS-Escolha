"""Módulo apps."""

from __future__ import annotations

from django.apps import AppConfig


class EscolhasConfig(AppConfig):
    """Registra a app Escolhas e carrega os signals na inicialização."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "escolhas"

    def ready(self) -> None:
        """Importa os signals quando a aplicação estiver pronta."""
