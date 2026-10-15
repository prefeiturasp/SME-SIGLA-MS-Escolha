"""Serializers para importação de escolhas da Prodam."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ..constants import SituacaoChoices


class EscolhaProdamItemSerializer(serializers.Serializer):
    """Escolha de um candidato no resultado de convocação da Prodam."""

    cpf = serializers.CharField(
        required=True,
        max_length=14,
        help_text=(
            "CPF do candidato, no mesmo formato cadastrado no "
            "MS-Candidatos."
        ),
    )
    codigo_cargo = serializers.CharField(
        required=True,
        help_text=(
            "Código numérico do cargo, como texto. Com o código EOL, "
            "identifica a vaga escolhida."
        ),
    )
    codigo_eol = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=(
            "Código EOL da escola escolhida, completado com zeros à "
            "esquerda até 6 dígitos. Sem ele, ou se não há vaga do cargo "
            "na escola, a escolha fica sem vaga."
        ),
    )
    tipo_vaga = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=(
            "`D` para vaga definitiva ou `P` para precária. Qualquer outro "
            "valor deixa a escolha sem tipo de vaga."
        ),
    )
    situacao = serializers.CharField(
        required=True,
        help_text=(
            "`ESCOLHA`, `NAO-ESCOLHA` ou `RECONVOCACAO`, em maiúsculas ou "
            "minúsculas. `PENDENTE` e qualquer outro texto são gravados "
            "como `nao-escolha`."
        ),
    )


class EscolhasProdamImportacaoSerializer(serializers.Serializer):
    """Escolhas da Prodam a importar para um processo de convocação."""

    concurso_uuid = serializers.UUIDField(
        required=True, help_text="UUID do concurso das escolhas."
    )
    processo_uuid = serializers.UUIDField(
        required=True,
        help_text=(
            "UUID do processo de convocação. Só os habilitados convocados "
            "nele são encontrados pelo CPF."
        ),
    )
    escolhas = serializers.ListField(
        child=EscolhaProdamItemSerializer(),
        required=True,
        allow_empty=False,
        help_text="Escolhas a importar. Cada item é processado em separado.",
    )

    def validate_escolhas(self, value: Any) -> Any:
        """Garante CPF, codigo_cargo e situacao em cada item."""
        for escolha in value:
            if not escolha.get("cpf"):
                raise serializers.ValidationError(
                    "CPF é obrigatório em cada escolha"
                )
            if not escolha.get("codigo_cargo"):
                raise serializers.ValidationError(
                    "codigo_cargo é obrigatório em cada escolha"
                )
            if not escolha.get("situacao"):
                raise serializers.ValidationError(
                    "situacao é obrigatória em cada escolha"
                )
        return value


class EscolhaImportadaSerializer(serializers.Serializer):
    """Escolha criada pela importação."""

    uuid = serializers.UUIDField(help_text="Identificador da escolha criada.")
    candidato_uuid = serializers.UUIDField(
        help_text="UUID do habilitado encontrado pelo CPF."
    )
    situacao = serializers.ChoiceField(
        choices=SituacaoChoices.choices,
        help_text="Situação gravada na escolha.",
    )


class ErroImportacaoProdamSerializer(serializers.Serializer):
    """Motivo pelo qual um item da importação não virou escolha."""

    index = serializers.IntegerField(
        help_text="Posição do item na lista enviada, a partir de 0."
    )
    cpf = serializers.CharField(help_text="CPF do item.")
    erro = serializers.CharField(help_text="Mensagem que descreve a falha.")


class ImportacaoProdamRespostaSerializer(serializers.Serializer):
    """Resultado da importação de escolhas da Prodam."""

    escolhas_criadas = serializers.IntegerField(
        help_text="Quantidade de escolhas criadas."
    )
    escolhas = EscolhaImportadaSerializer(
        many=True, help_text="Escolhas criadas, na ordem dos itens enviados."
    )
    erros = ErroImportacaoProdamSerializer(
        many=True,
        required=False,
        help_text="Itens que falharam. Presente só quando há falhas.",
    )
