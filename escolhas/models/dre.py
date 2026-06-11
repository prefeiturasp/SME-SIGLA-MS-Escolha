"""Módulo models/dre."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel


class Dre(BaseModel):
    """Model para armazenar dados da DRE."""

    codigo = models.CharField(max_length=20, verbose_name="Código da DRE")
    nome = models.CharField(max_length=255, verbose_name="Nome da DRE")
    sigla = models.CharField(max_length=50, verbose_name="Sigla da DRE")

    class Meta:
        """Representa Meta."""

        db_table = "dres"
        verbose_name = "DRE"
        verbose_name_plural = "DREs"
        ordering = ["nome"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.sigla} - {self.nome}"


auditlog.register(Dre)
