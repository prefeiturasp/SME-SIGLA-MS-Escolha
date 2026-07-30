"""Repositório de acesso a dados de parametrização.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from parametrizacao.models import Parametrizacao


class ParametrizacaoRepository:
    """Acesso aos dados de parametrização de tipos de UE."""

    @classmethod
    def listar_tipos_ue_ativos(cls) -> list[str]:
        """Lista tipos de UE com flag usar=True."""
        return list(
            Parametrizacao.objects.filter(usar=True).values_list(
                "tipo_ue", flat=True
            )
        )

    @classmethod
    def listar_tipos_ue_bloqueados(cls) -> set[str]:
        """Conjunto de tipos de UE com flag usar=False."""
        return set(
            Parametrizacao.objects.filter(usar=False).values_list(
                "tipo_ue", flat=True
            )
        )

    @classmethod
    def listar_tipos_ue_existentes(cls) -> set[str]:
        """Conjunto de tipos de UE já cadastrados."""
        return set(Parametrizacao.objects.values_list("tipo_ue", flat=True))

    @classmethod
    def listar_todos(cls) -> list[dict[str, Any]]:
        """Lista todas as parametrizações serializadas."""
        itens = list(Parametrizacao.objects.all().order_by("tipo_ue"))
        return cls.montar_lista_resposta(itens)

    @classmethod
    def obter_por_uuid(
        cls, item_uuid: str | UUID
    ) -> dict[str, Any] | None:
        """Busca parametrização pelo UUID serializada."""
        item = Parametrizacao.objects.filter(uuid=item_uuid).first()
        return cls.montar_resposta(item) if item else None

    @classmethod
    def bulk_atualizar_usar(cls, by_uuid: dict[str, bool]) -> int:
        """Atualiza o campo usar em lote.

        Args:
            by_uuid: Mapa uuid → valor de usar.

        Returns:
            Quantidade de registros atualizados.
        """
        if not by_uuid:
            return 0
        updates = []
        for item in Parametrizacao.objects.filter(
            uuid__in=list(by_uuid.keys())
        ):
            item.usar = by_uuid.get(str(item.uuid), item.usar)
            updates.append(item)
        if not updates:
            return 0
        Parametrizacao.objects.bulk_update(updates, ["usar"])
        return len(updates)

    @classmethod
    def sincronizar_a_partir_de_escolas(cls) -> int:
        """Garante registro para cada tipo_ue distinto em Escola.

        Returns:
            Quantidade de registros criados.
        """
        from escola.repository import EscolaRepository

        tipos_distintos = EscolaRepository.listar_tipos_ue_distintos()
        existentes = cls.listar_tipos_ue_existentes()
        novos = [
            Parametrizacao(tipo_ue=tipo)
            for tipo in tipos_distintos
            if tipo not in existentes
        ]
        if novos:
            Parametrizacao.objects.bulk_create(novos)
        return len(novos)

    @staticmethod
    def montar_resposta(item: Parametrizacao) -> dict[str, Any]:
        """Transforma uma parametrização em dicionário de resposta."""
        from parametrizacao.serializers import ParametrizacaoSerializer

        return ParametrizacaoSerializer(item).data

    @classmethod
    def montar_lista_resposta(
        cls, itens: list[Parametrizacao]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de parametrizações em dicionários."""
        from parametrizacao.serializers import ParametrizacaoSerializer

        return ParametrizacaoSerializer(itens, many=True).data
