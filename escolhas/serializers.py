from rest_framework import serializers
from .models import Escolha, Escola, Dre


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


class DreSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Dre."""
    class Meta:
        model = Dre
        fields = ['uuid', 'codigo', 'nome', 'sigla']


class EscolaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Escola."""
    dre = DreSerializer(read_only=True)
    class Meta:
        model = Escola
        fields = [
            'uuid', 'dre', 'codigo_eol', 'nome_oficial', 'nome_nao_oficial',
            'tipo_unidade_admin', 'tipo_ue', 'logradouro', 'numero', 'bairro',
            'cep', 'distrito', 'sub_prefeitura', 'nome_dre', 'email',
            'telefone1', 'telefone2', 'ano_construcao', 'propriedade',
            'capacidade_vagas_matutino', 'capacidade_vagas_vespertino',
            'capacidade_vagas_noturno', 'capacidade_vagas_intermediario',
            'capacidade_vagas_integral', 'capacidade_vagas_total',
            'organizacao_parceira', 'quantidade_de_funcionarios', 'status',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']


class EscolaSelectSerializer(serializers.ModelSerializer):
    value = serializers.UUIDField(source='uuid')
    label = serializers.CharField(source='nome_oficial')

    class Meta:
        model = Escola
        fields = ['value', 'label']


class EscolaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escola
        fields = ['uuid', 'codigo_eol', 'nome_oficial', 'status']
