"""Módulo serializers/parametrizacao."""
from rest_framework import serializers

from ..models import Parametrizacao


class ParametrizacaoSerializer(serializers.ModelSerializer):
    """Define ParametrizacaoSerializer."""
    class Meta:
        """Define Meta."""
        model = Parametrizacao
        fields = ["uuid", "tipo_ue", "usar", "criado_em", "atualizado_em"]
        read_only_fields = ["uuid", "tipo_ue", "criado_em", "atualizado_em"]


class ParametrizacaoBulkItemSerializer(serializers.Serializer):
    """Valida itens de atualização em massa para Parametrizacao.

    Apenas o campo 'usar' é atualizável; 'uuid' identifica o registro.
    """

    uuid = serializers.UUIDField()
    usar = serializers.BooleanField()
