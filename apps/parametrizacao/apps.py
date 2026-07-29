"""Configuração do app Django ``parametrizacao``."""

from django.apps import AppConfig


class ParametrizacaoConfig(AppConfig):
    """App de parametrização de tipos de UE."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "parametrizacao"
