from rest_framework import serializers

from ..models import Dre, Escola, VagasEscolas


class DreSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dre
        fields = ["uuid", "codigo", "nome", "sigla"]


class EscolaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para exibir apenas dados básicos da escola."""

    dre = DreSimpleSerializer(read_only=True)

    class Meta:
        model = Escola
        fields = [
            "codigo_eol",
            "codigo_integracao",
            "nome_oficial",
            "dre",
            "tipo_ue",
        ]


class VagasEscolasSerializer(serializers.ModelSerializer):
    escola = EscolaSimpleSerializer(read_only=True)
    lote_uuid = serializers.UUIDField(source="lote.uuid", read_only=True)

    class Meta:
        model = VagasEscolas
        fields = [
            "uuid",
            "lote_uuid",
            "data_fechamento_modulo",
            "cargo_codigo",
            "cargo_descricao",
            "vagas_precarias",
            "vagas_precarias_utilizadas",
            "vagas_precarias_restantes",
            "vagas_definitivas",
            "vagas_definitivas_utilizadas",
            "vagas_definitivas_restantes",
            "foi_utilizada",
            "esta_checada",
            "status",
            "escola",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]


class VagasEscolasInclusaoSerializer(serializers.Serializer):
    """Serializer para inclusão de vagas em um lote já existente.

    Diferente da criação, não exige ``concurso_uuid`` pois o lote (e seu
    concurso) já existe; aqui apenas adicionamos novas vagas a ele.
    """

    processo_uuid = serializers.UUIDField(
        error_messages={
            "invalid": "Deve ser um UUID válido.",
            "required": "Este campo é obrigatório.",
            "null": "Este campo não pode ser nulo.",
        }
    )
    processo_nome = serializers.CharField(allow_blank=True, required=False)
    vagas = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )

    def validate_vagas(self, value):
        """Valida a lista de vagas e converte status descritivos."""
        if not value:
            raise serializers.ValidationError(
                "A lista de vagas não pode estar vazia."
            )

        for i, vaga in enumerate(value):
            required_fields = [
                "data_fechamento_modulo",
                "cargo_codigo",
                "cargo_descricao",
                "codigo_eol",
                "vagas_precarias",
                "vagas_definitivas",
                "status",
            ]

            for field in required_fields:
                if field not in vaga:
                    raise serializers.ValidationError(
                        f"Campo '{field}' é obrigatório na vaga {i+1}."
                    )

        return value


class VagasEscolasCreateSerializer(VagasEscolasInclusaoSerializer):
    """Serializer para criação de vagas em lote.

    Exige ``concurso_uuid`` pois cria um novo lote vinculado ao concurso.
    """

    concurso_uuid = serializers.UUIDField(
        error_messages={
            "invalid": "Deve ser um UUID válido.",
            "required": "Este campo é obrigatório.",
            "null": "Este campo não pode ser nulo.",
        }
    )


class VagasEscolasUtilizadasUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VagasEscolas
        fields = [
            "vagas_precarias_utilizadas",
            "vagas_definitivas_utilizadas",
            "foi_utilizada",
            "esta_checada",
        ]


class VagaEscolaUtilizadaItemSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    foi_utilizada = serializers.BooleanField(required=True)
    vagas_precarias_utilizadas = serializers.IntegerField(required=False)
    vagas_definitivas_utilizadas = serializers.IntegerField(required=False)


class VagasEscolasUtilizadasBulkSerializer(serializers.Serializer):
    # Agora recebemos diretamente uma lista de itens (sem processo_uuid e sem chave 'vagas')  # noqa: E501
    # Este serializer pode ser usado para validação de cada item individualmente quando necessário  # noqa: E501
    pass
