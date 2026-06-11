from auditlog.registry import auditlog
from django.db import models

from .base import BaseModel


class VagasEscolasLote(BaseModel):
    processo_uuid = models.UUIDField(verbose_name="UUID do Processo")
    concurso_uuid = models.UUIDField(
        verbose_name="UUID do Concurso", null=True, blank=True
    )
    processo_nome = models.CharField(
        max_length=255, verbose_name="Nome do Processo", blank=True
    )

    class Meta:
        db_table = "vagas_escolas_lote"
        verbose_name = "Lote de Vagas do Processo"
        verbose_name_plural = "Lotes de Vagas dos Processos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.processo_nome} ({self.processo_uuid})"


auditlog.register(VagasEscolasLote)
