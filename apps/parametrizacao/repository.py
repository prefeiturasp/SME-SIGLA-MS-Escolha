"""Repositório de acesso a dados de parametrização."""

from __future__ import annotations

import logging

from parametrizacao.models import Parametrizacao

logger = logging.getLogger(__name__)


class ParametrizacaoRepository:
    """Acesso aos dados de parametrização de tipos de UE."""

    @classmethod
    def listar_tipos_ue_ativos(cls) -> list[str]:
        """Lista tipos de UE com flag usar=True."""
        logger.info("Listando tipos de UE ativos (usar=True)")
        return list(
            Parametrizacao.objects.filter(usar=True).values_list(
                "tipo_ue", flat=True
            )
        )

    @classmethod
    def listar_tipos_ue_bloqueados(cls) -> set[str]:
        """Conjunto de tipos de UE com flag usar=False."""
        logger.info("Listando tipos de UE bloqueados (usar=False)")
        return set(
            Parametrizacao.objects.filter(usar=False).values_list(
                "tipo_ue", flat=True
            )
        )

    @classmethod
    def listar_tipos_ue_existentes(cls) -> set[str]:
        """Conjunto de tipos de UE já cadastrados."""
        logger.info("Listando tipos de UE existentes")
        return set(Parametrizacao.objects.values_list("tipo_ue", flat=True))

    @classmethod
    def bulk_atualizar_usar(cls, by_uuid: dict[str, bool]) -> int:
        """Atualiza o campo usar em lote.

        Args:
            by_uuid: Mapa uuid → valor de usar.

        Returns:
            Quantidade de registros atualizados.
        """
        logger.info(
            f"Atualizando campo usar em lote para {len(by_uuid)} registro(s)"
        )
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
        logger.info("Sincronizando parametrização a partir das escolas")
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
