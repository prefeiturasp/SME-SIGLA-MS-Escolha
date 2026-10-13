"""Serializers da extração de dados de escolhas."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ..constants import SituacaoChoices

DESCRICOES_CONTAGEM = {
    "escolha": "Escolhas em que o candidato escolheu uma vaga.",
    "nao-escolha": "Escolhas em que o candidato não escolheu vaga.",
    "reconvocacao": "Escolhas em situação de reconvocação.",
}


class ExtracaoDadosFiltroSerializer(serializers.Serializer):
    """Recorte de um ano na extração de dados de escolhas."""

    ano = serializers.IntegerField(
        min_value=1000,
        max_value=9999,
        help_text="Ano dos processos de convocação, com 4 dígitos.",
    )
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text=(
            "Processos de convocação do ano. Quando informados, as "
            "escolhas com vaga entram pelo processo do lote da vaga, e as "
            "sem vaga, pelo ano de criação. Sem eles, vale o ano de "
            "criação de todas."
        ),
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Recorte da extração de dados de escolhas."""

    concurso_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=(
            "Restringe a extração ao concurso. Sem ele, entram todos os "
            "concursos."
        ),
    )
    filtros = ExtracaoDadosFiltroSerializer(
        many=True,
        required=False,
        default=list,
        max_length=2,
        help_text=(
            "Até dois anos a extrair. Quando informado e não vazio, a "
            "resposta vem separada por ano."
        ),
    )


class ContagemPorCategoriaSerializer(serializers.Serializer):
    """Quantidade de escolhas, no total e por categoria do candidato."""

    total = serializers.IntegerField(
        help_text=(
            "Quantidade de escolhas. Pode superar a soma das categorias: "
            "escolhas de candidatos sem categoria no MS-Candidatos, ou "
            "feitas quando ele não respondeu, só entram aqui."
        )
    )
    geral = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `GERAL`."
    )
    pcd = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `PCD`."
    )
    nna = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `NNA`."
    )


class _ContagensPorSituacaoSerializer(serializers.Serializer):
    """Base com uma contagem por situação da escolha."""

    contagens_obrigatorias = True

    def get_fields(self) -> dict[str, Any]:
        """Publica uma contagem por situação, com a chave da resposta."""
        contagens = {
            situacao: ContagemPorCategoriaSerializer(
                required=self.contagens_obrigatorias,
                help_text=DESCRICOES_CONTAGEM[situacao],
            )
            for situacao in SituacaoChoices.values
        }
        return {**contagens, **super().get_fields()}


class DreExtracaoSerializer(serializers.Serializer):
    """Escolhas realizadas e vagas ofertadas em uma DRE."""

    nome = serializers.CharField(help_text="Nome da DRE.")
    escolhas = serializers.IntegerField(
        help_text=("Escolhas na situação `escolha` com vaga em escola da DRE.")
    )
    vagas = serializers.IntegerField(
        help_text="Soma das vagas definitivas e precárias ofertadas na DRE."
    )


class DreCargoExtracaoSerializer(DreExtracaoSerializer):
    """Escolhas realizadas e vagas ofertadas em uma DRE, para um cargo."""

    codigo_cargo = serializers.IntegerField(
        help_text="Código numérico do cargo na SME."
    )
    cargo_descricao = serializers.CharField(help_text="Nome do cargo.")
    ultima_escolha_em = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text=(
            "Data e hora, em UTC, da escolha mais recente da DRE no cargo. "
            "Ausente quando há vagas e nenhuma escolha."
        ),
    )


class ExtracaoDadosAnoSerializer(_ContagensPorSituacaoSerializer):
    """Totais de escolhas de um ano."""

    dres = DreExtracaoSerializer(
        many=True, help_text="Escolhas e vagas do ano, por DRE."
    )


class FiltroAplicadoSerializer(serializers.Serializer):
    """Recorte de um ano, como foi aplicado na extração."""

    ano = serializers.IntegerField(help_text="Ano extraído.")
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Processos de convocação considerados no ano.",
    )


class ExtracaoDadosRespostaSerializer(_ContagensPorSituacaoSerializer):
    """Totais de escolhas e de vagas do recorte pedido.

    Sem `filtros`, as contagens por situação e `dres` vêm na raiz. Com
    `filtros`, saem da raiz e entra uma chave por ano informado, além de
    `filtros` e, se enviado, `concurso_uuid`.
    """

    contagens_obrigatorias = False

    concurso_uuid = serializers.UUIDField(
        required=False,
        help_text=(
            "Concurso do recorte. Presente só com `filtros` e quando foi "
            "enviado."
        ),
    )
    filtros = FiltroAplicadoSerializer(
        many=True,
        required=False,
        help_text=(
            "Anos extraídos, em ordem crescente. Presente só com `filtros`."
        ),
    )
    dres = DreExtracaoSerializer(
        many=True,
        required=False,
        help_text="Escolhas e vagas por DRE. Presente só sem `filtros`.",
    )
    dres_concursos = serializers.DictField(
        child=DreCargoExtracaoSerializer(many=True),
        help_text=(
            "Escolhas e vagas por DRE e cargo. Cada chave é o UUID de um "
            "concurso."
        ),
    )
    ultima_escolha_em = serializers.DateTimeField(
        allow_null=True,
        help_text=(
            "Data e hora, em UTC, da escolha com vaga mais recente do "
            "recorte, ou nulo se não há nenhuma."
        ),
    )
