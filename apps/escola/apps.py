"""Configuração do app Django ``escola``."""

from django.apps import AppConfig


class EscolaConfig(AppConfig):
    """App de DREs e escolas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "escola"
