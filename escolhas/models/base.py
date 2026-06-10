"""Módulo models/base."""

import uuid

from django.db import models


class BaseModel(models.Model):
    """Model base com UUID, criado_em e atualizado_em."""

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )

    class Meta:
        """Representa Meta."""

        abstract = True
