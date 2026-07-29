"""Módulo serializers/escola."""

from rest_framework import serializers

from ..models import Escola
from .dre import DreSerializer


class EscolaSerializer(serializers.ModelSerializer):
    """Escola completa com dados da DRE aninhada."""

    dre = DreSerializer(read_only=True)

    class Meta:
        """Representa Meta."""

        model = Escola
        fields = [
            "uuid",
            "dre",
            "codigo_eol",
            "nome_oficial",
            "nome_nao_oficial",
            "tipo_unidade_admin",
            "tipo_ue",
            "logradouro",
            "numero",
            "bairro",
            "cep",
            "distrito",
            "sub_prefeitura",
            "nome_dre",
            "email",
            "telefone1",
            "telefone2",
            "ano_construcao",
            "propriedade",
            "capacidade_vagas_matutino",
            "capacidade_vagas_vespertino",
            "capacidade_vagas_noturno",
            "capacidade_vagas_intermediario",
            "capacidade_vagas_integral",
            "capacidade_vagas_total",
            "organizacao_parceira",
            "quantidade_de_funcionarios",
            "status",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["uuid", "criado_em", "atualizado_em"]


class EscolaSelectSerializer(serializers.ModelSerializer):
    """Formata escola como par value/label para selects."""

    value = serializers.UUIDField(source="uuid")
    label = serializers.CharField(source="nome_oficial")  # type: ignore[assignment]

    class Meta:
        """Representa Meta."""

        model = Escola
        fields = ["value", "label"]


class EscolaListSerializer(serializers.ModelSerializer):
    """Listagem resumida (uuid, EOL, nome e status)."""

    class Meta:
        """Representa Meta."""

        model = Escola
        fields = ["uuid", "codigo_eol", "nome_oficial", "status"]
