from rest_framework import serializers
from ..models import VagasEscolas, Escola, Dre


class DreSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dre
        fields = ['uuid', 'codigo', 'nome']


class EscolaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para exibir apenas dados básicos da escola."""
    dre = DreSimpleSerializer(read_only=True)
    class Meta:
        model = Escola
        fields = ['codigo_eol', 'nome_oficial', 'dre']


class VagasEscolasSerializer(serializers.ModelSerializer):
    escola = EscolaSimpleSerializer(read_only=True)
    lote_uuid = serializers.UUIDField(source='lote.uuid', read_only=True)
    
    class Meta:
        model = VagasEscolas
        fields = [
            'uuid', 'lote_uuid', 'data_fechamento_modulo', 'cargo_codigo', 'cargo_descricao',
            'vagas_precarias', 'vagas_definitivas', 'status', 'escola',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['uuid', 'criado_em', 'atualizado_em']


class VagasEscolasCreateSerializer(serializers.Serializer):
    """Serializer para criação de vagas em lote."""
    processo_uuid = serializers.UUIDField()
    processo_nome = serializers.CharField(allow_blank=True, required=False)
    vagas = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    
    def validate_vagas(self, value):
        """Valida a lista de vagas e converte status descritivos."""
        if not value:
            raise serializers.ValidationError("A lista de vagas não pode estar vazia.")
        
        for i, vaga in enumerate(value):
            required_fields = [
                'data_fechamento_modulo', 'cargo_codigo', 'cargo_descricao',
                'codigo_eol', 'vagas_precarias', 'vagas_definitivas', 'status'
            ]
            
            for field in required_fields:
                if field not in vaga:
                    raise serializers.ValidationError(
                        f"Campo '{field}' é obrigatório na vaga {i+1}."
                    )
        
        return value
