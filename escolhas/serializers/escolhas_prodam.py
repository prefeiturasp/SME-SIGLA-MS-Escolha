"""Serializers para importação de escolhas da Prodam."""
from __future__ import annotations
from typing import Any
from rest_framework import serializers

class EscolhaProdamItemSerializer(serializers.Serializer):
    """Serializer para item de escolha da Prodam."""
    cpf = serializers.CharField(required=True, max_length=14)
    codigo_cargo = serializers.CharField(required=True)
    codigo_eol = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tipo_vaga = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    situacao = serializers.CharField(required=True)

class EscolhasProdamImportacaoSerializer(serializers.Serializer):
    """Serializer para validar dados de importação de escolhas da Prodam."""
    concurso_uuid = serializers.UUIDField(required=True)
    processo_uuid = serializers.UUIDField(required=True)
    escolhas = serializers.ListField(child=EscolhaProdamItemSerializer(), required=True, allow_empty=False)

    def validate_escolhas(self, value: Any) -> Any:
        """Valida que cada escolha tem os campos obrigatórios."""
        for escolha in value:
            if not escolha.get('cpf'):
                raise serializers.ValidationError('CPF é obrigatório em cada escolha')
            if not escolha.get('codigo_cargo'):
                raise serializers.ValidationError('codigo_cargo é obrigatório em cada escolha')
            if not escolha.get('situacao'):
                raise serializers.ValidationError('situacao é obrigatória em cada escolha')
        return value
