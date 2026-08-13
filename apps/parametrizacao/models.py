"""Módulo models/parametrizacao."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models

from core.models import BaseModel


class Parametrizacao(BaseModel):
    """Parametriza o uso de tipos de unidade escolar (tipo_ue) no sistema."""

    tipo_ue = models.CharField(
        max_length=255, unique=True, db_index=True, verbose_name="Tipo UE"
    )
    usar = models.BooleanField(
        default=False, verbose_name="Utilizar este tipo de UE"
    )

    class Meta:
        """Representa Meta."""

        # Mantém o label histórico das migrations em ``escolhas``.
        app_label = "escolhas"
        db_table = "escolhas_parametrizacao"
        verbose_name = "Parametrização de Tipo UE"
        verbose_name_plural = "Parametrizações de Tipos UE"
        ordering = ["tipo_ue"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.tipo_ue} ({('usar' if self.usar else 'não usar')})"

    @classmethod
    def sync_from_escolas(cls) -> int:
        """Garante registro para cada tipo_ue distinto em Escola.

        Returns:
            Valor inteiro resultante do cálculo.
        """
        from parametrizacao.repository import ParametrizacaoRepository

        return ParametrizacaoRepository.sincronizar_a_partir_de_escolas()


auditlog.register(Parametrizacao)
