"""Módulo models/parametrizacao."""

from __future__ import annotations

from typing import Any

from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel


class Parametrizacao(BaseModel):
    """Parametriza o uso de tipos de unidade escolar (tipo_ue) no sistema."""

    tipo_ue = models.CharField(
        max_length=255, unique=True, db_index=True, verbose_name="Tipo UE"
    )
    usar = models.BooleanField(
        default=False, verbose_name="Utilizar este tipo de UE"
    )

    class Meta:
        """Define Meta."""

        db_table = "escolhas_parametrizacao"
        verbose_name = "Parametrização de Tipo UE"
        verbose_name_plural = "Parametrizações de Tipos UE"
        ordering = ["tipo_ue"]

    def __str__(self) -> Any:
        """Executa   str  .

        Args:
            self: Instância do objeto.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        return f'{self.tipo_ue} ({('usar' if self.usar else 'não usar')})'

    @classmethod
    def sync_from_escolas(cls) -> int:
        """Garante que exista um registro para cada tipo_ue distinto em Escola.

        Args:
            cls: Classe referenciada.

        Returns:
            Valor inteiro calculado.

        Raises:
            Nenhuma exceção específica documentada.
        """
        from .escola import Escola

        qs = (
            Escola.objects.exclude(tipo_ue__isnull=True)
            .exclude(tipo_ue="")
            .order_by("tipo_ue")
            .values_list("tipo_ue", flat=True)
            .distinct()
        )
        tipos_distintos = list(qs)
        existentes = set(cls.objects.values_list("tipo_ue", flat=True))
        novos = []
        for tipo in tipos_distintos:
            if tipo in existentes:
                continue
            novos.append(cls(tipo_ue=tipo))
        if novos:
            cls.objects.bulk_create(novos)  # type: ignore[arg-type]
        return len(novos)


auditlog.register(Parametrizacao)
