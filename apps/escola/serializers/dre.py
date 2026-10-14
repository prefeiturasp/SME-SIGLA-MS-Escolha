"""Módulo serializers/dre."""

from rest_framework import serializers

from core.serializers import PaginaSerializer

from ..models import Dre
from .descricoes import DESCRICOES_DRE


class DreSerializer(serializers.ModelSerializer):
    """Diretoria Regional de Educação."""

    class Meta:
        """Representa Meta."""

        model = Dre
        fields = ["uuid", "codigo", "nome", "sigla"]
        extra_kwargs = DESCRICOES_DRE


class DrePaginadaSerializer(PaginaSerializer):
    """Página da listagem de DREs."""

    results = DreSerializer(many=True, help_text="DREs da página.")
