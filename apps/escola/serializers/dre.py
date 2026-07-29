"""Módulo serializers/dre."""

from rest_framework import serializers

from ..models import Dre


class DreSerializer(serializers.ModelSerializer):
    """DRE com uuid, código, nome e sigla."""

    class Meta:
        """Representa Meta."""

        model = Dre
        fields = ["uuid", "codigo", "nome", "sigla"]
