"""Módulo serializers/vagas_escolas."""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from core.serializers import ErrosValidacaoSerializer
from escola.models import Dre, Escola
from escola.serializers.descricoes import DESCRICOES_DRE, DESCRICOES_ESCOLA
from vagas_escolas.models import VagasEscolas

DESCRICOES_VAGA = {
    "uuid": {"help_text": "Identificador da vaga."},
    "data_fechamento_modulo": {
        "help_text": (
            "Data de fechamento do módulo da escola, informada no envio "
            "das vagas."
        )
    },
    "cargo_codigo": {"help_text": "Código numérico do cargo na SME."},
    "cargo_descricao": {"help_text": "Nome do cargo."},
    "vagas_precarias": {
        "help_text": "Quantidade de vagas precárias ofertadas."
    },
    "vagas_precarias_utilizadas": {
        "help_text": (
            "Vagas precárias que o processo de convocação vai usar, ou "
            "nulo enquanto não foram informadas."
        )
    },
    "vagas_precarias_restantes": {
        "help_text": (
            "Vagas precárias ainda livres. Começa igual a "
            "`vagas_precarias` e diminui a cada escolha criada."
        )
    },
    "vagas_definitivas": {
        "help_text": "Quantidade de vagas definitivas ofertadas."
    },
    "vagas_definitivas_utilizadas": {
        "help_text": (
            "Vagas definitivas que o processo de convocação vai usar, ou "
            "nulo enquanto não foram informadas."
        )
    },
    "vagas_definitivas_restantes": {
        "help_text": (
            "Vagas definitivas ainda livres. Começa igual a "
            "`vagas_definitivas` e diminui a cada escolha criada."
        )
    },
    "foi_utilizada": {
        "help_text": "Indica se a vaga foi marcada para uso no processo."
    },
    "esta_checada": {
        "help_text": (
            "Indica se a vaga está selecionada. A listagem de vagas só "
            "traz as que têm `true`."
        )
    },
    "status": {
        "help_text": (
            "Situação da vaga, em texto. As opções previstas são `1` "
            "(ativo), `0` (inativo), `2` (suspenso) e `3` (cancelado), e "
            "só elas são aceitas ao alterar uma vaga. O envio em lote "
            "grava o valor recebido sem conferir, e por isso há vagas "
            "com outros textos, como `ativo`."
        )
    },
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}


class DreSimpleSerializer(serializers.ModelSerializer):
    """DRE da escola em que a vaga é ofertada."""

    class Meta:
        """Representa Meta."""

        model = Dre
        fields = ["uuid", "codigo", "nome", "sigla"]
        extra_kwargs = DESCRICOES_DRE


class EscolaSimpleSerializer(serializers.ModelSerializer):
    """Dados de identificação da escola em que a vaga é ofertada."""

    dre = DreSimpleSerializer(read_only=True, help_text="DRE da escola.")

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
        extra_kwargs = DESCRICOES_ESCOLA


class VagasEscolasSerializer(serializers.ModelSerializer):
    """Vagas de um cargo em uma escola, dentro do lote de um processo."""

    escola = EscolaSimpleSerializer(
        read_only=True,
        help_text=(
            "Escola em que a vaga é ofertada. Somente leitura: não pode "
            "ser alterada pela API."
        ),
    )
    lote_uuid = serializers.UUIDField(
        source="lote.uuid",
        read_only=True,
        help_text="UUID do lote do processo a que a vaga pertence.",
    )

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
        extra_kwargs = DESCRICOES_VAGA


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

    def validate_vagas(self, value: Any) -> Any:
        """Exige lista não vazia com campos obrigatórios por vaga."""
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
    """Atualiza vagas utilizadas e flags de checagem."""

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
    """Uso de uma vaga no processo de convocação."""

    uuid = serializers.UUIDField(
        help_text=(
            "UUID da vaga. UUIDs que não existem voltam em "
            "`nao_encontrados`."
        )
    )
    foi_utilizada = serializers.BooleanField(
        required=True,
        help_text=(
            "Indica se a vaga será usada. O mesmo valor é gravado em "
            "`esta_checada`: com `false`, a vaga sai da listagem."
        ),
    )
    vagas_precarias_utilizadas = serializers.IntegerField(
        required=False,
        help_text=(
            "Vagas precárias que serão usadas. Se omitido, o valor atual "
            "é mantido."
        ),
    )
    vagas_definitivas_utilizadas = serializers.IntegerField(
        required=False,
        help_text=(
            "Vagas definitivas que serão usadas. Se omitido, o valor "
            "atual é mantido."
        ),
    )


class VagasEscolasUtilizadasBulkSerializer(serializers.Serializer):
    """Reservado para atualização em massa de vagas utilizadas."""

    pass


class DreDaListagemSerializer(serializers.Serializer):
    """DRE que tem vagas na listagem."""

    codigo = serializers.CharField(help_text="Código da DRE na SME.")
    nome = serializers.CharField(help_text="Nome da DRE.")
    uuid = serializers.UUIDField(help_text="Identificador da DRE.")


@extend_schema_serializer(many=False)
class VagasEscolasListagemSerializer(serializers.Serializer):
    """Vagas selecionadas, com os totais e as DREs envolvidas."""

    vagas = VagasEscolasSerializer(
        many=True,
        help_text=(
            "Vagas com `esta_checada` verdadeiro que atendem aos filtros."
        ),
    )
    total_vagas = serializers.IntegerField(
        help_text=(
            "Soma de `total_vagas_precarias` e `total_vagas_definitivas`."
        )
    )
    total_vagas_precarias = serializers.IntegerField(
        help_text=(
            "Soma das vagas precárias. Usa as quantidades utilizadas se "
            "alguma vaga da listagem já as tem; do contrário, as ofertadas."
        )
    )
    total_vagas_definitivas = serializers.IntegerField(
        help_text=(
            "Soma das vagas definitivas, pela mesma regra de "
            "`total_vagas_precarias`."
        )
    )
    dres = DreDaListagemSerializer(
        many=True,
        help_text="DREs das escolas listadas, em ordem de código.",
    )


class VagaLoteItemSerializer(serializers.Serializer):
    """Vagas de um cargo em uma escola, como enviadas em um lote."""

    data_fechamento_modulo = serializers.DateField(
        help_text="Data de fechamento do módulo da escola, em `AAAA-MM-DD`."
    )
    cargo_codigo = serializers.IntegerField(
        help_text="Código numérico do cargo na SME."
    )
    cargo_descricao = serializers.CharField(help_text="Nome do cargo.")
    codigo_eol = serializers.CharField(
        help_text=(
            "Código EOL da escola, enviado como texto. É completado com "
            "zeros à esquerda até 6 dígitos."
        )
    )
    vagas_precarias = serializers.IntegerField(
        help_text="Quantidade de vagas precárias ofertadas."
    )
    vagas_definitivas = serializers.IntegerField(
        help_text="Quantidade de vagas definitivas ofertadas."
    )
    status = serializers.CharField(
        help_text=(
            "Situação da vaga, com até 20 caracteres. O valor é gravado "
            "como enviado, sem conferir as opções do campo: `1` (ativo), "
            "`0` (inativo), `2` (suspenso) e `3` (cancelado)."
        )
    )


class VagasLoteRequisicaoSerializer(serializers.Serializer):
    """Vagas de um processo de convocação, enviadas de uma vez."""

    processo_uuid = serializers.UUIDField(
        help_text="UUID do processo de convocação."
    )
    processo_nome = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nome do processo, gravado no lote quando ele é criado.",
    )
    concurso_uuid = serializers.UUIDField(
        help_text="UUID do concurso do processo."
    )
    vagas = VagaLoteItemSerializer(
        many=True,
        allow_empty=False,
        help_text="Vagas a gravar. Cada item é processado em separado.",
    )


class ErroVagaLoteSerializer(serializers.Serializer):
    """Motivo pelo qual uma vaga do lote não foi gravada."""

    vaga_index = serializers.IntegerField(
        help_text="Posição da vaga na lista enviada, a partir de 1."
    )
    codigo_eol = serializers.CharField(
        required=False,
        help_text=(
            "Código EOL procurado. Presente quando a escola não foi "
            "encontrada."
        ),
    )
    error = serializers.CharField(help_text="Mensagem que descreve a falha.")


class VagasLoteRespostaSerializer(serializers.Serializer):
    """Resultado do processamento de um lote de vagas."""

    mensagem = serializers.CharField(help_text="Resumo do resultado.")
    vagas_criadas = serializers.IntegerField(
        help_text="Quantidade de vagas gravadas."
    )
    total_processadas = serializers.IntegerField(
        help_text="Quantidade de vagas recebidas."
    )
    lote_uuid = serializers.UUIDField(
        help_text="UUID do lote em que as vagas foram gravadas."
    )
    processo_uuid = serializers.UUIDField(
        help_text="UUID do processo de convocação."
    )
    erros = ErroVagaLoteSerializer(
        many=True,
        required=False,
        help_text="Vagas que falharam. Presente só quando há falhas.",
    )
    vagas_com_erro = serializers.IntegerField(
        required=False,
        help_text=(
            "Quantidade de vagas que falharam. Presente só quando há "
            "falhas."
        ),
    )


class ErrosVagasLoteSerializer(serializers.Serializer):
    """Corpo de lote recusado antes de qualquer gravação."""

    def get_fields(self) -> dict[str, Any]:
        """Publica ``errors``, nome que a classe já usa para outro fim."""
        return {
            "errors": ErrosValidacaoSerializer(
                help_text="Erros de validação do corpo, por campo."
            )
        }


class ErroVagasLoteSerializer(serializers.Serializer):
    """Lote de vagas interrompido, com o código do motivo."""

    detail = serializers.CharField(help_text="Mensagem que descreve o erro.")
    code = serializers.CharField(
        help_text=(
            "Código do motivo: `TIPO_UE_DESABILITADO` quando o lote traz "
            "escola de um tipo de unidade desabilitado, ou "
            "`ERRO_AO_CRIAR_VAGAS_EM_LOTE` em falha inesperada."
        )
    )


class VagasUtilizadasRespostaSerializer(serializers.Serializer):
    """Resultado da atualização das vagas utilizadas."""

    atualizados = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs das vagas encontradas e gravadas.",
    )
    nao_encontrados = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs enviados que não correspondem a nenhuma vaga.",
    )
    total = serializers.IntegerField(help_text="Quantidade de vagas gravadas.")


class LotesExcluidosSerializer(serializers.Serializer):
    """Resultado da exclusão das vagas de um processo."""

    lotes_excluidos = serializers.IntegerField(
        help_text=(
            "Quantidade de registros apagados, somando os lotes do "
            "processo e as vagas de cada um."
        )
    )
