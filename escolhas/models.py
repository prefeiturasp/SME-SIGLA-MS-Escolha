import uuid
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class BaseModel(models.Model):
    """
    Model base com UUID, criado_em e atualizado_em.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        abstract = True

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
