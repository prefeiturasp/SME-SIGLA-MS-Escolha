"""Módulo serializers/parametrizacao."""

from rest_framework import serializers

from ..models import Parametrizacao


class ParametrizacaoSerializer(serializers.ModelSerializer):
    """Serializer do modelo Parametrizacao."""

    class Meta:
        """Representa Meta."""

        model = Parametrizacao
        fields = ["uuid", "tipo_ue", "usar", "criado_em", "atualizado_em"]
        read_only_fields = ["uuid", "tipo_ue", "criado_em", "atualizado_em"]


class ParametrizacaoBulkItemSerializer(serializers.Serializer):
    """Valida itens de atualização em massa para Parametrizacao."""

    uuid = serializers.UUIDField()
    usar = serializers.BooleanField()
