from rest_framework import serializers
from ..models import Escolha


class EscolhaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Escolha.
    """
    class Meta:
        model = Escolha
        fields = [
            'uuid',
            'candidato_uuid',
            'situacao',
            'tipo_vaga',
            'e_retardatario',
            'vaga_escola_uuid',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']
        extra_kwargs = {
            'candidato_uuid': {'allow_null': False, 'required': True},
            'situacao': {'required': True},
            'tipo_vaga': {'allow_null': False, 'required': True},
            'vaga_escola_uuid': {'allow_null': False, 'required': True},
        }


class EscolhaSelectSerializer(serializers.ModelSerializer):
    """
    Serializer para selects/dropdowns no frontend.
    """
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='situacao')

    class Meta:
        model = Escolha
        fields = ['value', 'label']


class EscolhaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listagem de escolhas.
    """
    class Meta:
        model = Escolha
        fields = [
            'uuid',
            'candidato_uuid',
            'situacao',
            'tipo_vaga',
            'e_retardatario',
            'vaga_escola_uuid',
            'criado_em',
            'atualizado_em',
        ]
