from django.db import models
from django.utils.translation import gettext_lazy as _


class SituacaoChoices(models.TextChoices):
    """
    Choices para situação da escolha.
    """
    ESCOLHA = 'escolha', _('Escolha')
    NAO_ESCOLHA = 'nao-escolha', _('Não escolha')
    RECONVOCACAO = 'reconvocacao', _('Reconvocação')


class TipoVagaChoices(models.TextChoices):
    """
    Choices para tipo de vaga.
    """
    DEFINITIVA = 'definitiva', _('Definitiva')
    PRECARIA = 'precaria', _('Precária')

