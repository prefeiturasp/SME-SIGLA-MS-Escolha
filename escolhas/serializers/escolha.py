"""Módulo serializers/escolha."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from ..choices import SituacaoChoices
from ..models import Escolha, HistoricoEscolha, VagasEscolas
from .vagas_escolas import VagasEscolasSerializer


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Define DynamicFieldsSerializer."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Executa   init  .

        Args:
            self: Instância do objeto.
            *args: Argumentos posicionais variáveis.
            **kwargs: Argumentos nomeados variáveis.

        Raises:
            Nenhuma exceção específica documentada.
        """
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class HistoricoEscolhaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo HistoricoEscolha (histórico de mudanças de."""

    class Meta:
        """Define Meta."""

        model = HistoricoEscolha
        fields = ["uuid", "situacao_anterior", "situacao_nova", "criado_em"]
        read_only_fields = ["uuid", "criado_em"]


class EscolhaSerializer(DynamicFieldsSerializer):
    """Serializer para o modelo Escolha."""

    vaga_escola_uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="UUID da vaga da escola. Será convertido para ForeignKey internamente.",  # noqa: E501
    )

    class Meta:
        """Define Meta."""

        model = Escolha
        fields = [
            "uuid",
            "candidato_uuid",
            "concurso_uuid",
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
            "candidato_uuid": {"allow_null": False, "required": True},
            "concurso_uuid": {"allow_null": False, "required": True},
            "situacao": {"required": True},
            "tipo_vaga": {"allow_null": True, "required": False},
        }

    def to_representation(self, instance: Any) -> Any:
        """Converte a ForeignKey vaga_escola para UUID na representação.

        Args:
            self: Instância do objeto.
            instance: Instância do modelo em atualização.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        data = super().to_representation(instance)
        if instance.vaga_escola:
            data["vaga_escola_uuid"] = str(instance.vaga_escola.uuid)
        else:
            data["vaga_escola_uuid"] = None
        return data

    def validate(self, attrs: Any) -> Any:
        """Validação customizada: tipo_vaga e vaga_escola são obrigatórios.

        Args:
            self: Instância do objeto.
            attrs: Atributos em validação.

        Returns:
            Resultado da operação.

        Raises:
            ValidationError: Se ocorrer erro nesta operação.
        """
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
                vaga_escola = VagasEscolas.objects.get(uuid=vaga_escola_uuid)
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
        """Define Meta."""

        model = Escolha
        fields = ["value", "label"]


class EscolhaListSerializer(DynamicFieldsSerializer):
    """Serializer para listagem de escolhas."""

    vaga_escola_uuid = serializers.SerializerMethodField()
    vaga_escola = VagasEscolasSerializer(read_only=True)
    historico = HistoricoEscolhaSerializer(many=True, read_only=True)

    class Meta:
        """Define Meta."""

        model = Escolha
        fields = [
            "uuid",
            "candidato_uuid",
            "situacao",
            "tipo_vaga",
            "e_retardatario",
            "vaga_escola_uuid",
            "vaga_escola",
            "historico",
            "criado_em",
            "atualizado_em",
        ]

    def get_vaga_escola_uuid(self, obj: Any) -> Any:
        """Retorna o UUID da vaga_escola se existir.

        Args:
            self: Instância do objeto.
            obj: Parâmetro obj.

        Returns:
            Valor calculado para o campo ou propriedade.

        Raises:
            Nenhuma exceção específica documentada.
        """
        return str(obj.vaga_escola.uuid) if obj.vaga_escola else None


class EscolhaReconvocacaoSerializer(serializers.ModelSerializer):
    """Serializer para reconvocação, retorna apenas uuid e candidato_uuid."""

    class Meta:
        """Define Meta."""

        model = Escolha
        fields = ["uuid", "candidato_uuid"]
