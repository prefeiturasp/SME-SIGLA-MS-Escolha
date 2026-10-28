"""Módulo serializers/escolha."""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.serializers import PaginaSerializer
from vagas_escolas.models import VagasEscolas
from vagas_escolas.repository import VagasEscolasRepository
from vagas_escolas.serializers import VagasEscolasSerializer

from ..constants import SituacaoChoices
from ..models import Escolha, HistoricoEscolha
from .descricoes import DESCRICOES_ESCOLHA, DESCRICOES_HISTORICO


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Serializa modelos com restrição opcional de campos."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Remove campos não listados em fields, se informado."""
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class HistoricoEscolhaSerializer(serializers.ModelSerializer):
    """Mudança de situação de uma escolha."""

    class Meta:
        """Representa Meta."""

        model = HistoricoEscolha
        fields = ["uuid", "situacao_anterior", "situacao_nova", "criado_em"]
        read_only_fields = ["uuid", "criado_em"]
        extra_kwargs = DESCRICOES_HISTORICO


class EscolhaSerializer(DynamicFieldsSerializer):
    """Escolha de vaga de um candidato em um concurso."""

    vaga_escola_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text=(
            "UUID da vaga escolhida. Obrigatório quando a situação é "
            "`escolha`. Enviar nulo não desfaz o vínculo com a vaga atual."
        ),
    )
    vaga_escola: serializers.SlugRelatedField[VagasEscolas] = (
        serializers.SlugRelatedField(
            slug_field="uuid",
            read_only=True,
            allow_null=True,
            label="Vaga da Escola",
            help_text=DESCRICOES_ESCOLHA["vaga_escola"]["help_text"],
        )
    )

    class Meta:
        """Representa Meta."""

        model = Escolha
        fields = [
            "uuid",
            "candidato_uuid",
            "concurso_uuid",
            "processo_uuid",
            "situacao",
            "tipo_vaga",
            "e_retardatario",
            "vaga_escola_uuid",
            "vaga_escola",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = [
            "uuid",
            "criado_em",
            "atualizado_em",
            "vaga_escola",
        ]
        extra_kwargs = {
            **DESCRICOES_ESCOLHA,
            "candidato_uuid": {
                **DESCRICOES_ESCOLHA["candidato_uuid"],
                "allow_null": False,
                "required": True,
            },
            "concurso_uuid": {
                **DESCRICOES_ESCOLHA["concurso_uuid"],
                "allow_null": False,
                "required": True,
            },
            "processo_uuid": {
                **DESCRICOES_ESCOLHA["processo_uuid"],
                "allow_null": True,
                "required": False,
            },
            "situacao": {**DESCRICOES_ESCOLHA["situacao"], "required": True},
            "tipo_vaga": {
                **DESCRICOES_ESCOLHA["tipo_vaga"],
                "allow_null": True,
                "required": False,
            },
        }

    def to_representation(self, instance: Any) -> Any:
        """Converte a ForeignKey vaga_escola para UUID na representação."""
        data = super().to_representation(instance)
        if instance.vaga_escola:
            data["vaga_escola_uuid"] = str(instance.vaga_escola.uuid)
        else:
            data["vaga_escola_uuid"] = None
        return data

    def validate(self, attrs: Any) -> Any:
        """Validação customizada: tipo_vaga e vaga_escola são obrigatórios."""
        situacao = attrs.get("situacao")
        if self.instance:
            tipo_vaga = attrs.get("tipo_vaga", self.instance.tipo_vaga)  # type: ignore[union-attr]
            vaga_escola_uuid = attrs.get("vaga_escola_uuid")
            vaga_escola = attrs.get("vaga_escola", self.instance.vaga_escola)  # type: ignore[union-attr]
            if not situacao:
                situacao = self.instance.situacao  # type: ignore[union-attr]
        else:
            tipo_vaga = attrs.get("tipo_vaga")
            vaga_escola_uuid = attrs.get("vaga_escola_uuid")
            vaga_escola = attrs.get("vaga_escola")
        if vaga_escola_uuid and (not vaga_escola):
            try:
                vaga_escola = VagasEscolasRepository.obter_por_uuid(
                    vaga_escola_uuid
                )
                attrs["vaga_escola"] = vaga_escola
            except VagasEscolas.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "vaga_escola_uuid": (
                            f"VagaEscola com UUID {vaga_escola_uuid} "
                            "não encontrada."
                        )
                    }
                ) from None
        attrs.pop("vaga_escola_uuid", None)
        if situacao == SituacaoChoices.ESCOLHA:
            if not tipo_vaga:
                raise serializers.ValidationError(
                    {
                        "tipo_vaga": 'Este campo é obrigatório quando a situação é "escolha".'  # noqa: E501
                    }
                )
            if not vaga_escola:
                raise serializers.ValidationError(
                    {
                        "vaga_escola_uuid": 'Este campo é obrigatório quando a situação é "escolha".'  # noqa: E501
                    }
                )
        return attrs


class EscolhaSelectSerializer(serializers.ModelSerializer):
    """Serializer para selects/dropdowns no frontend."""

    value = serializers.UUIDField(source="uuid")
    label = serializers.CharField(source="situacao")  # type: ignore[assignment]

    class Meta:
        """Representa Meta."""

        model = Escolha
        fields = ["value", "label"]


class EscolhaDetalheSerializer(EscolhaSerializer):
    """Escolha de vaga de um candidato em um concurso."""

    vaga_escola_uuid = serializers.UUIDField(
        read_only=True,
        allow_null=True,
        help_text=(
            "UUID da vaga escolhida, ou nulo se não há vaga. Repete "
            "`vaga_escola` e vem mesmo quando `fields` não o pede."
        ),
    )


class EscolhaListSerializer(DynamicFieldsSerializer):
    """Escolha com os dados da vaga e o histórico de situações."""

    vaga_escola_uuid = serializers.SerializerMethodField(
        help_text="UUID da vaga escolhida, ou nulo se não há vaga."
    )
    vaga_escola = VagasEscolasSerializer(
        read_only=True,
        allow_null=True,
        help_text=(
            "Vaga escolhida, com a escola e a DRE, ou nulo se não há vaga."
        ),
    )
    historico = HistoricoEscolhaSerializer(
        many=True,
        read_only=True,
        help_text="Mudanças de situação, da mais recente para a mais antiga.",
    )

    class Meta:
        """Representa Meta."""

        model = Escolha
        fields = [
            "uuid",
            "candidato_uuid",
            "concurso_uuid",
            "processo_uuid",
            "situacao",
            "tipo_vaga",
            "e_retardatario",
            "vaga_escola_uuid",
            "vaga_escola",
            "historico",
            "criado_em",
            "atualizado_em",
        ]
        extra_kwargs = DESCRICOES_ESCOLHA

    @extend_schema_field(
        {"type": "string", "format": "uuid", "nullable": True}
    )
    def get_vaga_escola_uuid(self, obj: Any) -> Any:
        """Expõe UUID da vaga_escola na listagem, ou None se ausente."""
        return str(obj.vaga_escola.uuid) if obj.vaga_escola else None


class EscolhaReconvocacaoSerializer(serializers.ModelSerializer):
    """Escolha em situação de reconvocação, só com os identificadores."""

    class Meta:
        """Representa Meta."""

        model = Escolha
        fields = ["uuid", "candidato_uuid"]
        extra_kwargs = DESCRICOES_ESCOLHA


class EscolhaPaginadaSerializer(PaginaSerializer):
    """Página da listagem de escolhas."""

    results = EscolhaListSerializer(many=True, help_text="Escolhas da página.")
