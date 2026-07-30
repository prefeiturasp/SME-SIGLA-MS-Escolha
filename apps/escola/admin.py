"""Configuração do Django Admin para DREs e escolas."""

from django.contrib import admin

from escola.models import Dre, Escola


@admin.register(Dre)
class DreAdmin(admin.ModelAdmin):
    """Configuração do admin para Dre."""

    list_display = [
        "sigla",
        "codigo",
        "nome",
        "uuid",
        "criado_em",
        "atualizado_em",
    ]
    search_fields = ["codigo", "nome", "sigla"]
    list_filter = ["criado_em", "atualizado_em"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["nome"]


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    """Configuração do admin para Escola."""

    list_display = [
        "nome_oficial",
        "codigo_eol",
        "dre",
        "tipo_ue",
        "status",
        "uuid",
        "criado_em",
        "atualizado_em",
    ]
    search_fields = [
        "nome_oficial",
        "codigo_eol",
        "nome_dre",
        "bairro",
        "distrito",
    ]
    list_filter = [
        "dre",
        "tipo_ue",
        "status",
        "sub_prefeitura",
        "distrito",
        "criado_em",
    ]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["nome_oficial"]
