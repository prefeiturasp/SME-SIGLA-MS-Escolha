from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..choices import SituacaoChoices
from .base import BaseModel


class HistoricoEscolha(BaseModel):
    """
    Model para histórico de mudanças de situação das escolhas.
    """

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
        db_table = "historico_escolhas"
        verbose_name = "Histórico de Escolha"
        verbose_name_plural = "Históricos de Escolhas"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.escolha.uuid} - {self.situacao_anterior} -> {self.situacao_nova}"  # noqa: E501


auditlog.register(HistoricoEscolha)
