"""Configuração do Django Admin para vagas de escolas."""

from django.contrib import admin

from vagas_escolas.models import VagasEscolas, VagasEscolasLote


@admin.register(VagasEscolasLote)
class VagasEscolasLoteAdmin(admin.ModelAdmin):
    """Configuração do admin para VagasEscolasLote."""

    list_display = ["processo_nome", "processo_uuid", "criado_em"]
    search_fields = ["processo_nome", "processo_uuid", "criado_em"]
    list_filter = ["criado_em"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["-criado_em"]


@admin.register(VagasEscolas)
class VagasEscolasAdmin(admin.ModelAdmin):
    """Configuração do admin para VagasEscolas."""

    list_display = [
        "escola",
        "criado_em",
        "data_fechamento_modulo",
        "cargo_codigo",
        "cargo_descricao",
        "vagas_precarias",
        "vagas_precarias_utilizadas",
        "vagas_definitivas",
        "vagas_definitivas_utilizadas",
        "status",
        "lote",
    ]
    search_fields = [
        "escola__nome_oficial",
        "escola__codigo_eol",
        "cargo_descricao",
        "lote",
    ]
    list_filter = [
        "criado_em",
        "status",
        "data_fechamento_modulo",
        "escola__dre",
        "lote",
    ]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["-data_fechamento_modulo"]
