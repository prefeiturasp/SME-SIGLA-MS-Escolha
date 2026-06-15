"""Módulo models/vagas_escolas."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel
from .escola import Escola
from .vagas_lote import VagasEscolasLote


class VagasEscolas(BaseModel):
    """Vagas definitivas e precárias de um cargo em escola/lote."""

    STATUS_CHOICES = [
        ("1", "Ativo"),
        ("0", "Inativo"),
        ("2", "Suspenso"),
        ("3", "Cancelado"),
    ]
    lote = models.ForeignKey(
        VagasEscolasLote,
        on_delete=models.CASCADE,
        related_name="vagas",
        verbose_name="Lote do Processo",
        null=True,
        blank=True,
    )
    data_fechamento_modulo = models.DateField(
        verbose_name="Data de Fechamento do Módulo"
    )
    cargo_codigo = models.IntegerField(verbose_name="Código do Cargo")
    cargo_descricao = models.CharField(
        max_length=200, verbose_name="Descrição do Cargo"
    )
    vagas_precarias = models.IntegerField(
        verbose_name="Vagas Precárias", default=0
    )
    vagas_precarias_utilizadas = models.IntegerField(
        verbose_name="Vagas Precárias Utilizadas", null=True, blank=True
    )
    vagas_precarias_restantes = models.IntegerField(
        verbose_name="Vagas Precárias Restantes", default=0
    )
    vagas_definitivas = models.IntegerField(
        verbose_name="Vagas Definitivas", default=0
    )
    vagas_definitivas_utilizadas = models.IntegerField(
        verbose_name="Vagas Definitivas Utilizadas", null=True, blank=True
    )
    vagas_definitivas_restantes = models.IntegerField(
        verbose_name="Vagas Definitivas Restantes", default=0
    )
    foi_utilizada = models.BooleanField(
        verbose_name="Foi Utilizada", default=False
    )
    esta_checada = models.BooleanField(
        verbose_name="Está Checada", default=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="1",
        verbose_name="Status",
    )
    escola = models.ForeignKey(
        Escola,
        on_delete=models.CASCADE,
        verbose_name="Escola",
        related_name="vagas_escolas",
    )

    class Meta:
        """Representa Meta."""

        db_table = "vagas_escolas"
        verbose_name = "Vagas da Escola"
        verbose_name_plural = "Vagas das Escolas"
        ordering = ["-data_fechamento_modulo", "escola__nome_oficial"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.escola.nome_oficial} - {self.cargo_descricao}"


auditlog.register(VagasEscolas)
