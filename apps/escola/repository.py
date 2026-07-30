"""Repositório de acesso a dados de escolas e DREs.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from escola.models import Dre, Escola


class DreRepository:
    """Acesso aos dados de DREs."""

    @staticmethod
    def montar_resposta(dre: Dre) -> dict[str, Any]:
        """Transforma uma DRE em dicionário de resposta da API."""
        from escola.serializers import DreSerializer

        return DreSerializer(dre).data

    @classmethod
    def montar_lista_resposta(cls, dres: list[Dre]) -> list[dict[str, Any]]:
        """Transforma uma lista de DREs em dicionários de resposta."""
        from escola.serializers import DreSerializer

        return DreSerializer(dres, many=True).data

    @classmethod
    def listar_todos(cls) -> list[dict[str, Any]]:
        """Lista todas as DREs serializadas."""
        dres = list(Dre.objects.all().order_by("nome"))
        return cls.montar_lista_resposta(dres)

    @classmethod
    def obter_por_uuid(cls, dre_uuid: str | UUID) -> dict[str, Any] | None:
        """Busca uma DRE pelo UUID e devolve a resposta serializada."""
        dre = Dre.objects.filter(uuid=dre_uuid).first()
        return cls.montar_resposta(dre) if dre else None


class EscolaRepository:
    """Acesso aos dados de escolas."""

    @classmethod
    def obter_por_codigo_eol(cls, codigo_eol: str) -> Escola:
        """Busca escola pelo código EOL (modelo para persistência).

        Raises:
            Escola.DoesNotExist: Quando não há escola com o código.
        """
        return Escola.objects.get(codigo_eol=codigo_eol)

    @classmethod
    def obter_tipo_ue_por_codigo_eol(cls, codigo_eol: str) -> Escola:
        """Busca escola pelo EOL carregando apenas tipo_ue.

        Raises:
            Escola.DoesNotExist: Quando não há escola com o código.
        """
        return Escola.objects.only("tipo_ue").get(codigo_eol=codigo_eol)

    @classmethod
    def listar_tipos_ue_distintos(cls) -> list[str]:
        """Lista tipos de UE distintos cadastrados nas escolas."""
        return list(
            Escola.objects.exclude(tipo_ue__isnull=True)
            .exclude(tipo_ue="")
            .order_by("tipo_ue")
            .values_list("tipo_ue", flat=True)
            .distinct()
        )

    @staticmethod
    def montar_resposta(escola: Escola) -> dict[str, Any]:
        """Transforma uma escola em dicionário de resposta da API."""
        from escola.serializers import EscolaSerializer

        return EscolaSerializer(escola).data

    @classmethod
    def montar_lista_resposta(
        cls, escolas: list[Escola]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de escolas em dicionários de resposta."""
        from escola.serializers import EscolaSerializer

        return EscolaSerializer(escolas, many=True).data

    @classmethod
    def listar_todos(cls) -> list[dict[str, Any]]:
        """Lista todas as escolas com DRE serializadas."""
        escolas = list(
            Escola.objects.select_related("dre").all().order_by("-criado_em")
        )
        return cls.montar_lista_resposta(escolas)

    @classmethod
    def obter_por_uuid(cls, escola_uuid: str | UUID) -> dict[str, Any] | None:
        """Busca uma escola pelo UUID e devolve a resposta serializada."""
        escola = (
            Escola.objects.select_related("dre").filter(uuid=escola_uuid).first()
        )
        return cls.montar_resposta(escola) if escola else None
