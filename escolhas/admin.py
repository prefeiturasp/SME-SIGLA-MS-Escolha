"""
Django admin configuration for the concursos module.
"""
from django.contrib import admin
from .models import Escolha, VagasEscolas, Escola, Dre, VagasEscolasLote
 

@admin.register(Escolha)
class EscolhaAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Escolha.
    """
    list_display = ['nome', 'uuid', 'criado_em', 'atualizado_em']
    list_filter = ['criado_em', 'atualizado_em']
    search_fields = ['nome']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome',)
        }),
        ('Metadados', {
            'fields': ('uuid', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Dre)
class DreAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'codigo', 'nome', 'uuid', 'criado_em', 'atualizado_em']
    search_fields = ['codigo', 'nome', 'sigla']
    list_filter = ['criado_em', 'atualizado_em']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['nome']


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = [
        'nome_oficial', 'codigo_eol', 'dre', 'status',
        'uuid', 'criado_em', 'atualizado_em'
    ]
    search_fields = [
        'nome_oficial', 'codigo_eol', 'nome_dre', 'bairro', 'distrito'
    ]
    list_filter = ['dre', 'status', 'sub_prefeitura', 'distrito', 'criado_em']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['nome_oficial']


@admin.register(VagasEscolasLote)
class VagasEscolasLoteAdmin(admin.ModelAdmin):
    list_display = ['processo_nome', 'processo_uuid', 'criado_em']
    search_fields = ['processo_nome', 'processo_uuid', 'criado_em']
    list_filter = ['criado_em']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['-criado_em']


@admin.register(VagasEscolas)
class VagasEscolasAdmin(admin.ModelAdmin):
    list_display = [
        'escola', 'criado_em', 'data_fechamento_modulo', 'cargo_codigo', 'cargo_descricao',
        'vagas_precarias', 'vagas_precarias_utilizadas', 'vagas_definitivas', 'vagas_definitivas_utilizadas', 'status', 'lote'
    ]
    search_fields = ['escola__nome_oficial', 'escola__codigo_eol', 'cargo_descricao', 'lote']
    list_filter = ['criado_em', 'status', 'data_fechamento_modulo', 'escola__dre', 'lote']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['-data_fechamento_modulo']

