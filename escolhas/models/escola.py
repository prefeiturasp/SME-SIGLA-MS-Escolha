from django.db import models
from auditlog.registry import auditlog
from .base import BaseModel
from .dre import Dre


class Escola(BaseModel):
    dre = models.ForeignKey(Dre, on_delete=models.CASCADE, verbose_name="DRE")
    codigo_eol = models.CharField(max_length=20, verbose_name="Código EOL")
    nome_oficial = models.CharField(max_length=255, verbose_name="Nome Oficial")
    nome_nao_oficial = models.CharField(max_length=255, verbose_name="Nome Não Oficial", blank=True, null=True)
    tipo_unidade_admin = models.CharField(max_length=255, verbose_name="Tipo Unidade Administrativa")
    tipo_ue = models.CharField(max_length=255, verbose_name="Tipo UE")
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, verbose_name="Número")
    bairro = models.CharField(max_length=255, verbose_name="Bairro")
    cep = models.CharField(max_length=20, verbose_name="CEP")
    distrito = models.CharField(max_length=255, verbose_name="Distrito")
    sub_prefeitura = models.CharField(max_length=255, verbose_name="Subprefeitura")
    nome_dre = models.CharField(max_length=255, verbose_name="Nome da DRE")
    email = models.EmailField(max_length=255, verbose_name="Email", blank=True, null=True)
    telefone1 = models.CharField(max_length=30, verbose_name="Telefone 1", blank=True, null=True)
    telefone2 = models.CharField(max_length=30, verbose_name="Telefone 2", blank=True, null=True)
    ano_construcao = models.IntegerField(verbose_name="Ano de Construção", blank=True, null=True)
    propriedade = models.CharField(max_length=50, verbose_name="Propriedade")
    capacidade_vagas_matutino = models.IntegerField(verbose_name="Capacidade Vagas Matutino", default=0)
    capacidade_vagas_vespertino = models.IntegerField(verbose_name="Capacidade Vagas Vespertino", default=0)
    capacidade_vagas_noturno = models.IntegerField(verbose_name="Capacidade Vagas Noturno", default=0)
    capacidade_vagas_intermediario = models.IntegerField(verbose_name="Capacidade Vagas Intermediário", default=0)
    capacidade_vagas_integral = models.IntegerField(verbose_name="Capacidade Vagas Integral", default=0)
    capacidade_vagas_total = models.IntegerField(verbose_name="Capacidade Vagas Total", default=0)
    organizacao_parceira = models.BooleanField(verbose_name="Organização Parceira", default=False)
    quantidade_de_funcionarios = models.IntegerField(verbose_name="Quantidade de Funcionários", default=0)
    status = models.CharField(max_length=30, verbose_name="Status")

    class Meta:
        db_table = 'escolas'
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        ordering = ['nome_oficial']

    def __str__(self):
        return self.nome_oficial


auditlog.register(Escola)
