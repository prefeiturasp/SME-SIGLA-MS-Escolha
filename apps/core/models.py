"""Modelos compartilhados do projeto."""

import uuid

from django.db import models


class BaseModel(models.Model):
    """Model base com id padrão do Django e uuid público.

    Também traz criado_em e atualizado_em.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )

    class Meta:
        """Meta do BaseModel."""

        abstract = True
