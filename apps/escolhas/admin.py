"""Django admin configuration for the escolhas module."""

from django.contrib import admin

from escolhas.models import Escolha


@admin.register(Escolha)
class EscolhaAdmin(admin.ModelAdmin):
    """Admin para o modelo Escolha."""

    list_display = [
        "candidato_uuid",
        "situacao",
        "tipo_vaga",
        "e_retardatario",
        "vaga_escola",
        "uuid",
        "criado_em",
        "atualizado_em",
    ]
    list_filter = ["situacao", "tipo_vaga", "e_retardatario", "criado_em"]
    search_fields = ["candidato_uuid"]
    readonly_fields = ["uuid", "criado_em", "atualizado_em"]
    ordering = ["-criado_em"]

    fieldsets = (
        (
            "Informações da Escolha",
            {
                "fields": (
                    "candidato_uuid",
                    "situacao",
                    "tipo_vaga",
                    "e_retardatario",
                    "vaga_escola",
                )
            },
        ),
        (
            "Metadados",
            {
                "fields": ("uuid", "criado_em", "atualizado_em"),
                "classes": ("collapse",),
            },
        ),
    )
