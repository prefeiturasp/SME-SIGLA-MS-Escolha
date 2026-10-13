"""Módulo serializers/parametrizacao."""

from rest_framework import serializers

from parametrizacao.models import Parametrizacao

DESCRICOES_PARAMETRIZACAO = {
    "uuid": {"help_text": "Identificador da parametrização."},
    "tipo_ue": {
        "help_text": (
            "Tipo de unidade escolar, como consta no cadastro das escolas. "
            "Somente leitura."
        )
    },
    "usar": {
        "help_text": (
            "Indica se o tipo entra no fluxo de escolha. Escolas de um "
            "tipo com `false` não aparecem na API e bloqueiam a criação "
            "de lotes de vagas."
        )
    },
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}


class ParametrizacaoSerializer(serializers.ModelSerializer):
    """Habilitação de um tipo de unidade escolar no fluxo de escolha."""

    class Meta:
        """Representa Meta."""

        model = Parametrizacao
        fields = ["uuid", "tipo_ue", "usar", "criado_em", "atualizado_em"]
        read_only_fields = ["uuid", "tipo_ue", "criado_em", "atualizado_em"]
        extra_kwargs = DESCRICOES_PARAMETRIZACAO


class ParametrizacaoBulkItemSerializer(serializers.Serializer):
    """Novo valor de `usar` para uma parametrização."""

    uuid = serializers.UUIDField(
        help_text=(
            "UUID da parametrização. UUIDs que não existem são ignorados."
        )
    )
    usar = serializers.BooleanField(
        help_text="Indica se o tipo de unidade entra no fluxo de escolha."
    )


class ParametrizacoesCriadasSerializer(serializers.Serializer):
    """Resultado da sincronização com os tipos de unidade das escolas."""

    created = serializers.IntegerField(
        help_text=(
            "Quantidade de parametrizações criadas. Zero quando todos os "
            "tipos de unidade das escolas já estavam cadastrados."
        )
    )


class ParametrizacoesAtualizadasSerializer(serializers.Serializer):
    """Resultado da atualização em lote."""

    updated = serializers.IntegerField(
        help_text="Quantidade de parametrizações encontradas e gravadas."
    )
