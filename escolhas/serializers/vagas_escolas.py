"""Módulo serializers/vagas_escolas."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ..models import Dre, Escola, VagasEscolas


class DreSimpleSerializer(serializers.ModelSerializer):
    """Serializer do modelo DreSimple."""

    class Meta:
        """Representa Meta."""

        model = Dre
        fields = ["uuid", "codigo", "nome", "sigla"]


class EscolaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para exibir apenas dados básicos da escola."""

    dre = DreSimpleSerializer(read_only=True)

    class Meta:
        """Representa Meta."""

        model = Escola
        fields = [
            "codigo_eol",
            "codigo_integracao",
            "nome_oficial",
            "dre",
            "tipo_ue",
        ]


class VagasEscolasSerializer(serializers.ModelSerializer):
    """Serializer do modelo VagasEscolas."""

    escola = EscolaSimpleSerializer(read_only=True)
    lote_uuid = serializers.UUIDField(source="lote.uuid", read_only=True)

    class Meta:
        """Representa Meta."""

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


class VagasEscolasCreateSerializer(serializers.Serializer):
    """Serializer para criação de vagas em lote."""

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

    def validate_vagas(self, value: Any) -> Any:
        """Valida vagas."""
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
                        f"Campo '{field}' é obrigatório na vaga {i + 1}."
                    )
        return value


class VagasEscolasUtilizadasUpdateSerializer(serializers.ModelSerializer):
    """Serializer do modelo VagasEscolasUtilizadasUpdate."""

    class Meta:
        """Representa Meta."""

        model = VagasEscolas
        fields = [
            "vagas_precarias_utilizadas",
            "vagas_definitivas_utilizadas",
            "foi_utilizada",
            "esta_checada",
        ]


class VagaEscolaUtilizadaItemSerializer(serializers.Serializer):
    """Serializer do modelo VagaEscolaUtilizadaItem."""

    uuid = serializers.UUIDField()
    foi_utilizada = serializers.BooleanField(required=True)
    vagas_precarias_utilizadas = serializers.IntegerField(required=False)
    vagas_definitivas_utilizadas = serializers.IntegerField(required=False)


class VagasEscolasUtilizadasBulkSerializer(serializers.Serializer):
    """Serializer do modelo VagasEscolasUtilizadasBulk."""

    pass
