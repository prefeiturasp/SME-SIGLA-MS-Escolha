"""Módulo models/escolha."""

from __future__ import annotations

from typing import Any

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from ..constants import SituacaoChoices, TipoVagaChoices


class Escolha(BaseModel):
    """Registra escolha de vaga de candidato em concurso/processo."""

    history = AuditlogHistoryField()
    candidato_uuid = models.UUIDField(
        verbose_name=_("UUID do Candidato"), null=True, blank=True
    )
    concurso_uuid = models.UUIDField(
        verbose_name=_("UUID do Concurso"), null=True, blank=True
    )
    situacao = models.CharField(
        max_length=20,
        choices=SituacaoChoices.choices,
        default=SituacaoChoices.ESCOLHA,
        verbose_name="Situação",
    )
    tipo_vaga = models.CharField(
        max_length=20,
        choices=TipoVagaChoices.choices,
        verbose_name="Tipo de Vaga",
        null=True,
        blank=True,
    )
    e_retardatario = models.BooleanField(
        default=False, verbose_name=_("É retardatário")
    )
    vaga_escola = models.ForeignKey(
        "escolhas.VagasEscolas",
        on_delete=models.SET_NULL,
        related_name="escolhas",
        verbose_name=_("Vaga da Escola"),
        null=True,
        blank=True,
    )

    class Meta:
        """Representa Meta."""

        db_table = "escolhas"
        verbose_name = "Escolha"
        verbose_name_plural = "Escolhas"
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        vaga_uuid = self.vaga_escola.uuid if self.vaga_escola else "N/A"
        return f"{self.candidato_uuid} - {vaga_uuid}"


auditlog.register(Escolha)
