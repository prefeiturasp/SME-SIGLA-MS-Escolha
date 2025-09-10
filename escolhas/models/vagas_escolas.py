from django.db import models
from auditlog.registry import auditlog
from .base import BaseModel
from .escola import Escola


class VagasEscolas(BaseModel):
    STATUS_CHOICES = [
        ('1', 'Ativo'),
        ('0', 'Inativo'),
        ('2', 'Suspenso'),
        ('3', 'Cancelado'),
    ]

    data_fechamento_modulo = models.DateField(verbose_name="Data de Fechamento do Módulo")
    cargo_codigo = models.IntegerField(verbose_name="Código do Cargo")
    cargo_descricao = models.CharField(max_length=200, verbose_name="Descrição do Cargo")
    vagas_precarias = models.IntegerField(verbose_name="Vagas Precárias", default=0)
    vagas_definitivas = models.IntegerField(verbose_name="Vagas Definitivas", default=0)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='1',
        verbose_name="Status"
    )
    escola = models.ForeignKey(
        Escola, 
        on_delete=models.CASCADE, 
        verbose_name="Escola",
        related_name='vagas_escolas'
    )

    class Meta:
        db_table = 'vagas_escolas'
        verbose_name = 'Vagas da Escola'
        verbose_name_plural = 'Vagas das Escolas'
        ordering = ['-data_fechamento_modulo', 'escola__nome_oficial']

    def __str__(self):
        return f"{self.escola.nome_oficial} - {self.cargo_descricao}"


auditlog.register(VagasEscolas)
