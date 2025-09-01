"""
Django admin configuration for the concursos module.
"""
from django.contrib import admin
from .models import Cargo, Concurso, Escolha


# TODO REMOVE AFTER TEST
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Cargo.
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

# TODO REMOVE AFTER TEST
class CargoInline(admin.TabularInline):
    """
    Inline para mostrar cargos em concursos.
    """
    model = Concurso.cargos.through
    extra = 1
    verbose_name = "Cargo"
    verbose_name_plural = "Cargos"


# TODO REMOVE AFTER TEST
@admin.register(Concurso)
class ConcursoAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Concurso.
    """
    list_display = ['nome', 'uuid', 'cargos_count', 'criado_em', 'atualizado_em']
    list_filter = ['criado_em', 'atualizado_em']
    search_fields = ['nome']
    readonly_fields = ['uuid', 'criado_em', 'atualizado_em']
    ordering = ['-criado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome',)
        }),
        ('Cargos', {
            'fields': ('cargos',)
        }),
        ('Metadados', {
            'fields': ('uuid', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def cargos_count(self, obj):
        """
        Retorna o número de cargos associados ao concurso.
        """
        return obj.cargos.count()
    cargos_count.short_description = 'Número de Cargos'






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
