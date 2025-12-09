from django.db import models
from django.utils.translation import gettext_lazy as _
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ..choices import SituacaoChoices, TipoVagaChoices
from .base import BaseModel


class Escolha(BaseModel):
    """
    Model para escolhas.
    """

    history = AuditlogHistoryField()
    candidato_uuid = models.UUIDField(
        verbose_name=_('UUID do Candidato'),
        null=True,
        blank=True,
    )
    situacao = models.CharField(
        max_length=20,
        choices=SituacaoChoices.choices,
        default=SituacaoChoices.ESCOLHA,
        verbose_name='Situação',
    )
    tipo_vaga = models.CharField(
        max_length=20,
        choices=TipoVagaChoices.choices,
        verbose_name='Tipo de Vaga',
        null=True,
        blank=True,
    )
    e_retardatario = models.BooleanField(
        default=False,
        verbose_name=_('É retardatário'),
    )
    vaga_escola_uuid = models.UUIDField(
        verbose_name=_('UUID da Vaga da Escola'),
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'escolhas'
        verbose_name = 'Escolha'
        verbose_name_plural = 'Escolhas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.candidato_uuid} - {self.vaga_escola_uuid}"


auditlog.register(Escolha) 