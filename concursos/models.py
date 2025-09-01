import uuid
from django.db import models
from django.utils import timezone
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


class Cargo(BaseModel):
    """
    Model para cargos que podem ser associados a concursos.
    """
    history = AuditlogHistoryField()
    nome = models.CharField(max_length=200, verbose_name="Nome do Cargo")

    class Meta:
        db_table = 'cargos'
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Concurso(BaseModel):
    """
    Model para concursos que podem ter múltiplos cargos.
    """
    history = AuditlogHistoryField()
    nome = models.CharField(max_length=200, verbose_name="Nome do Concurso")
    cargos = models.ManyToManyField(
        Cargo, 
        verbose_name="Cargos",
        related_name="concursos"
    )

    class Meta:
        db_table = 'concursos'
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome
    





auditlog.register(Cargo)
auditlog.register(Concurso)
