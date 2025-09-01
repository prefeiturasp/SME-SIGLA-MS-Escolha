"""
Django admin configuration for the concursos module.
"""
from django.contrib import admin
from .models import Escolha

 

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
