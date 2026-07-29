"""Módulo models/historico_escolha."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..choices import SituacaoChoices
from core.models import BaseModel


class HistoricoEscolha(BaseModel):
    """Registra cada mudança de situação de uma escolha."""

    escolha = models.ForeignKey(
        "Escolha",
        on_delete=models.CASCADE,
        related_name="historico",
        verbose_name=_("Escolha"),
    )
    situacao_anterior = models.CharField(
        max_length=20,
        choices=SituacaoChoices.choices,
        blank=True,
        null=True,
        verbose_name=_("Situação Anterior"),
    )
    situacao_nova = models.CharField(
        max_length=20,
        choices=SituacaoChoices.choices,
        verbose_name=_("Situação Nova"),
    )

    class Meta:
        """Representa Meta."""

        db_table = "historico_escolhas"
        verbose_name = "Histórico de Escolha"
        verbose_name_plural = "Históricos de Escolhas"
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return (
            f"{self.escolha.uuid} - "
            f"{self.situacao_anterior} -> {self.situacao_nova}"
        )


auditlog.register(HistoricoEscolha)
