"""
Django admin configuration for the concursos module.
"""
from django.contrib import admin
from .models import Escolha
from .models.dre import Dre
from .models.escola import Escola
from .models.vagas_escolas import VagasEscolas

 

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


@admin.register(VagasEscolas)
class VagasEscolasAdmin(admin.ModelAdmin):
    list_display = [
        'escola', 'data_fechamento_modulo', 'cargo_codigo', 'cargo_descricao',
        'vagas_precarias', 'vagas_definitivas', 'status', 'uuid'
    ]
    search_fields = ['escola__nome_oficial', 'escola__codigo_eol', 'cargo_descricao']
    list_filter = ['status', 'data_fechamento_modulo', 'escola__dre']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['-data_fechamento_modulo']

