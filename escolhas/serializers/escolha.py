from rest_framework import serializers
from ..choices import SituacaoChoices
from ..models import Escolha, VagasEscolas
from .vagas_escolas import VagasEscolasSerializer


class EscolhaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Escolha.
    """
    # Campo customizado para aceitar UUID da vaga_escola e converter para ForeignKey
    vaga_escola_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text='UUID da vaga da escola. Será convertido para ForeignKey internamente.'
    )
    
    class Meta:
        model = Escolha
        fields = [
            'uuid',
            'candidato_uuid',
            'concurso_uuid',
            'situacao',
            'tipo_vaga',
            'e_retardatario',
            'vaga_escola_uuid',
            'vaga_escola',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em', 'vaga_escola']
        extra_kwargs = {
            'candidato_uuid': {'allow_null': False, 'required': True},
            'concurso_uuid': {'allow_null': False, 'required': True},
            'situacao': {'required': True},
            'tipo_vaga': {'allow_null': True, 'required': False},
        }
    
    def to_representation(self, instance):
        """
        Converte a ForeignKey vaga_escola para UUID na representação.
        """
        data = super().to_representation(instance)
        # Incluir o UUID da vaga_escola na resposta
        if instance.vaga_escola:
            data['vaga_escola_uuid'] = str(instance.vaga_escola.uuid)
        else:
            data['vaga_escola_uuid'] = None
        return data

    def validate(self, attrs):
        """
        Validação customizada: tipo_vaga e vaga_escola são obrigatórios
        apenas quando a situação for 'escolha'.
        """
        situacao = attrs.get('situacao')
        # Para atualizações parciais, usar valores do instance se não estiverem em attrs
        if self.instance:
            tipo_vaga = attrs.get('tipo_vaga', self.instance.tipo_vaga)
            vaga_escola_uuid = attrs.get('vaga_escola_uuid')
            vaga_escola = attrs.get('vaga_escola', self.instance.vaga_escola)
            if not situacao:
                situacao = self.instance.situacao
        else:
            tipo_vaga = attrs.get('tipo_vaga')
            vaga_escola_uuid = attrs.get('vaga_escola_uuid')
            vaga_escola = attrs.get('vaga_escola')
        
        # Converter UUID para ForeignKey se fornecido
        if vaga_escola_uuid and not vaga_escola:
            try:
                vaga_escola = VagasEscolas.objects.get(uuid=vaga_escola_uuid)
                attrs['vaga_escola'] = vaga_escola
            except VagasEscolas.DoesNotExist:
                raise serializers.ValidationError({
                    'vaga_escola_uuid': f'VagaEscola com UUID {vaga_escola_uuid} não encontrada.'
                })
        
        # Remover vaga_escola_uuid dos attrs para evitar erro
        attrs.pop('vaga_escola_uuid', None)

        if situacao == SituacaoChoices.ESCOLHA:
            if not tipo_vaga:
                raise serializers.ValidationError({
                    'tipo_vaga': 'Este campo é obrigatório quando a situação é "escolha".'
                })
            if not vaga_escola:
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
    Inclui dados completos de vaga_escola, escola e DRE.
    """
    vaga_escola_uuid = serializers.SerializerMethodField()
    vaga_escola = VagasEscolasSerializer(read_only=True)
    
    class Meta:
        model = Escolha
        fields = [
            'uuid',
            'candidato_uuid',
            'situacao',
            'tipo_vaga',
            'e_retardatario',
            'vaga_escola_uuid',
            'vaga_escola',
            'criado_em',
            'atualizado_em',
        ]
    
    def get_vaga_escola_uuid(self, obj):
        """Retorna o UUID da vaga_escola se existir."""
        return str(obj.vaga_escola.uuid) if obj.vaga_escola else None


class EscolhaReconvocacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para reconvocação, retorna apenas uuid e candidato_uuid.
    """
    class Meta:
        model = Escolha
        fields = ['uuid', 'candidato_uuid']
