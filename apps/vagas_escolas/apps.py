"""Configuração do app Django ``vagas_escolas``."""

from django.apps import AppConfig


class VagasEscolasConfig(AppConfig):
    """App de vagas de escolas e lotes."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "vagas_escolas"
