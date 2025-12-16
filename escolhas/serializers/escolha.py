from rest_framework import serializers
from ..choices import SituacaoChoices
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
            'tipo_vaga': {'allow_null': True, 'required': False},
            'vaga_escola_uuid': {'allow_null': True, 'required': False},
        }

    def validate(self, attrs):
        """
        Validação customizada: tipo_vaga e vaga_escola_uuid são obrigatórios
        apenas quando a situação for 'escolha'.
        """
        situacao = attrs.get('situacao')
        # Para atualizações parciais, usar valores do instance se não estiverem em attrs
        if self.instance:
            tipo_vaga = attrs.get('tipo_vaga', self.instance.tipo_vaga)
            vaga_escola_uuid = attrs.get('vaga_escola_uuid', self.instance.vaga_escola_uuid)
            if not situacao:
                situacao = self.instance.situacao
        else:
            tipo_vaga = attrs.get('tipo_vaga')
            vaga_escola_uuid = attrs.get('vaga_escola_uuid')

        if situacao == SituacaoChoices.ESCOLHA:
            if not tipo_vaga:
                raise serializers.ValidationError({
                    'tipo_vaga': 'Este campo é obrigatório quando a situação é "escolha".'
                })
            if not vaga_escola_uuid:
                raise serializers.ValidationError({
                    'vaga_escola_uuid': 'Este campo é obrigatório quando a situação é "escolha".'
                })

        return attrs


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


class EscolhaReconvocacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para reconvocação, retorna apenas uuid e candidato_uuid.
    """
    class Meta:
        model = Escolha
        fields = ['uuid', 'candidato_uuid']
