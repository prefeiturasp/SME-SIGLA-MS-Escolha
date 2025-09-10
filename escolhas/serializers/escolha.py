from rest_framework import serializers
from ..models import Escolha


class EscolhaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Escolha.
    """
    class Meta:
        model = Escolha
        fields = ['uuid', 'nome', 'criado_em', 'atualizado_em']
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']


class EscolhaSelectSerializer(serializers.ModelSerializer):
    """
    Serializer para selects/dropdowns no frontend.
    """
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='nome')

    class Meta:
        model = Escolha
        fields = ['value', 'label']


class EscolhaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de escolhas.
    """
    class Meta:
        model = Escolha
        fields = ['uuid', 'nome']
