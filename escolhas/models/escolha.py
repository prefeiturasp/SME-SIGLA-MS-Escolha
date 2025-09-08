import uuid
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from .base import BaseModel


class Escolha(BaseModel):
    """
    Model para escolhas .
    """
    history = AuditlogHistoryField()
    nome = models.CharField(max_length=200, verbose_name="Nome da Escolha")

    class Meta:
        db_table = 'escolhas'
        verbose_name = "Escolha"
        verbose_name_plural = "Escolhas"
        ordering = ['nome']

    def __str__(self):
        return self.nome


auditlog.register(Escolha) 