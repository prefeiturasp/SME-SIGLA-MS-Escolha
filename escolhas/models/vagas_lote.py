"""Módulo models/vagas_lote."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel


class VagasEscolasLote(BaseModel):
    """Agrupa vagas de escolas de um processo de convocação."""

    processo_uuid = models.UUIDField(verbose_name="UUID do Processo")
    processo_nome = models.CharField(
        max_length=255, verbose_name="Nome do Processo", blank=True
    )

    class Meta:
        """Representa Meta."""

        db_table = "vagas_escolas_lote"
        verbose_name = "Lote de Vagas do Processo"
        verbose_name_plural = "Lotes de Vagas dos Processos"
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.processo_nome} ({self.processo_uuid})"


auditlog.register(VagasEscolasLote)
