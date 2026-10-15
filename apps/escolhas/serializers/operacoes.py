"""Modelos de requisição e de resposta das consultas de escolhas."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ..constants import SituacaoChoices

DESCRICOES_POR_SITUACAO = {
    "escolha": "Candidatos que escolheram uma vaga.",
    "nao-escolha": "Candidatos que não escolheram vaga.",
    "reconvocacao": "Candidatos que voltam para uma nova convocação.",
}


class BuscaEscolhasRequisicaoSerializer(serializers.Serializer):
    """Candidatos cujas escolhas serão buscadas."""

    candidato_uuid = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text=(
            "UUIDs dos habilitados no MS-Candidatos. Sem o campo, ou com a "
            "lista vazia, a resposta vem vazia."
        ),
    )
    concurso_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Restringe a busca às escolhas do concurso.",
    )


class EscolhasPorConvocacaoRequisicaoSerializer(serializers.Serializer):
    """Processos de convocação cujas escolhas serão agregadas."""

    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="UUIDs dos processos de convocação. Ao menos um.",
    )


class CandidatosDaSituacaoSerializer(serializers.Serializer):
    """Candidatos de um processo cuja escolha está em uma situação."""

    total = serializers.IntegerField(
        help_text="Quantidade de escolhas na situação."
    )
    candidatos_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs dos habilitados, um por escolha.",
    )


class EscolhasDoProcessoSerializer(serializers.Serializer):
    """Candidatos de um processo, separados pela situação da escolha."""

    def get_fields(self) -> dict[str, Any]:
        """Publica um campo por situação, com a chave real da resposta."""
        return {
            situacao: CandidatosDaSituacaoSerializer(
                help_text=DESCRICOES_POR_SITUACAO[situacao]
            )
            for situacao in SituacaoChoices.values
        }


class EscolhasPorProcessoSerializer(serializers.Serializer):
    """Candidatos por processo de convocação e situação da escolha."""


class RepassadoDoMsCandidatosSerializer(serializers.Serializer):
    """Base dos modelos cujo corpo vem pronto do MS-Candidatos.

    Só os campos principais são descritos aqui. Os demais vêm como o
    MS-Candidatos os devolve.
    """


class HabilitacaoDoCandidatoSerializer(RepassadoDoMsCandidatosSerializer):
    """Participação do candidato em um concurso.

    Traz também os demais campos do habilitado no MS-Candidatos.
    """

    uuid = serializers.UUIDField(
        help_text=(
            "UUID do habilitado. É o valor usado em `candidato_uuid` nas "
            "escolhas."
        )
    )
    concurso_uuid = serializers.UUIDField(help_text="UUID do concurso.")
    concurso_nome = serializers.CharField(help_text="Nome do concurso.")
    codigo_cargo = serializers.CharField(
        help_text="Código numérico do cargo, como texto."
    )
    descricao_cargo = serializers.CharField(
        allow_blank=True,
        help_text=(
            "Nome do cargo. É trocado pelo nome cadastrado no MS-Concursos "
            "quando o código do cargo é encontrado lá."
        ),
    )
    classificacao = serializers.IntegerField(
        allow_null=True, help_text="Classificação na lista geral."
    )
    categoria_efetiva = serializers.CharField(
        allow_null=True,
        help_text=(
            "Lista pela qual o habilitado concorre: `GERAL`, `PCD` ou `NNA`."
        ),
    )
    eliminado = serializers.BooleanField(
        help_text="Indica se o habilitado foi eliminado do concurso."
    )


class CandidatoEncontradoSerializer(RepassadoDoMsCandidatosSerializer):
    """Candidato encontrado, com os concursos de que participa.

    Traz também os demais dados cadastrais do candidato no MS-Candidatos.
    """

    uuid = serializers.UUIDField(help_text="UUID do candidato.")
    nome = serializers.CharField(help_text="Nome do candidato.")
    cpf = serializers.CharField(help_text="CPF do candidato.")
    rg = serializers.CharField(allow_blank=True, help_text="RG do candidato.")
    registro_funcional = serializers.CharField(
        allow_blank=True,
        help_text="Registro funcional, se o candidato já é servidor.",
    )
    concursos = HabilitacaoDoCandidatoSerializer(
        many=True,
        help_text="Habilitações do candidato que casaram com a busca.",
    )
