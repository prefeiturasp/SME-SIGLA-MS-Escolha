"""Repositório de acesso a dados de escolhas.

Leituras públicas retornam dict / list[dict]. Métodos privados da extração
mantêm QuerySet internamente para compor filtros, agregações e values
antes de materializar o resultado em dict.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.db.models import Count, F, Max, Q, QuerySet

from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha, HistoricoEscolha

logger = logging.getLogger(__name__)


class EscolhaRepository:
    """Acesso aos dados de escolhas e histórico."""

    @classmethod
    def obter_por_pk(cls, pk: Any) -> Escolha:
        """Busca escolha pela PK.

        Raises:
            Escolha.DoesNotExist: Quando não encontrada.
        """
        logger.info(f"Buscando escolha pela PK: {pk}")
        return Escolha.objects.get(pk=pk)

    @classmethod
    def obter_por_candidato_e_concurso(
        cls, candidato_uuid: Any, concurso_uuid: Any
    ) -> Escolha | None:
        """Busca a primeira escolha do candidato no concurso."""
        logger.info(
            f"Buscando escolha: candidato_uuid={candidato_uuid}, "
            f"concurso_uuid={concurso_uuid}"
        )
        return Escolha.objects.filter(
            candidato_uuid=candidato_uuid, concurso_uuid=concurso_uuid
        ).first()

    @classmethod
    def criar(cls, **kwargs: Any) -> Escolha:
        """Persiste uma nova escolha."""
        logger.info(
            f"Criando escolha: candidato_uuid={kwargs.get('candidato_uuid')}, "
            f"concurso_uuid={kwargs.get('concurso_uuid')}"
        )
        return Escolha.objects.create(**kwargs)

    @classmethod
    def contar_por_cargo(cls) -> dict[str, int]:
        """Conta escolhas realizadas agrupadas por cargo."""
        logger.info("Contando escolhas realizadas agrupadas por cargo")
        qs = (
            Escolha.objects.filter(situacao=SituacaoChoices.ESCOLHA)
            .values("vaga_escola__cargo_codigo")
            .annotate(total=Count("uuid"))
            .order_by("vaga_escola__cargo_codigo")
        )
        return {
            str(item["vaga_escola__cargo_codigo"]): int(item["total"] or 0)
            for item in qs
        }

    @classmethod
    def criar_historico(
        cls,
        *,
        escolha: Escolha,
        situacao_anterior: str | None,
        situacao_nova: str,
    ) -> HistoricoEscolha:
        """Persiste um registro de histórico de escolha."""
        logger.info(
            f"Criando histórico da escolha pk={escolha.pk}: "
            f"{situacao_anterior} -> {situacao_nova}"
        )
        return HistoricoEscolha.objects.create(
            escolha=escolha,
            situacao_anterior=situacao_anterior,
            situacao_nova=situacao_nova,
        )

    @staticmethod
    def _serializar_datetime(value: Any) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @classmethod
    def _filtrar_escolhas_por_escopo(
        cls,
        qs: QuerySet,
        *,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> QuerySet:
        """Restringe escolhas ao escopo do filtro de extração.

        Com ``processo_uuids``, alinha ao ano do processo de convocação (como
        candidatos e vagas): escolhas com vaga pelo processo do lote; sem vaga,
        mantém ``criado_em`` no ano do filtro.
        """
        if processo_uuids:
            filtro_com_vaga = Q(
                vaga_escola__lote__processo_uuid__in=processo_uuids
            )
            filtro_sem_vaga = Q(vaga_escola__isnull=True)
            if concurso_uuid:
                filtro_com_vaga &= Q(concurso_uuid=concurso_uuid)
                filtro_sem_vaga &= Q(concurso_uuid=concurso_uuid)
            if ano:
                filtro_sem_vaga &= Q(criado_em__year=ano)
            qs = qs.filter(filtro_com_vaga | filtro_sem_vaga)
        else:
            if concurso_uuid:
                qs = qs.filter(concurso_uuid=concurso_uuid)
            if ano:
                qs = qs.filter(criado_em__year=ano)
        return qs

    @classmethod
    def buscar_escolhas_por_escopo(
        cls,
        *,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca escolhas no escopo, retornando candidato e situação.

        Args:
            concurso_uuid: Concurso a restringir; ausente → todos.
            ano: Ano do filtro (usado em ``criado_em`` quando sem processo).
            processo_uuids: Processos do ano; quando informados, filtra pelo
                processo do lote da vaga.

        Returns:
            Lista de ``{candidato_uuid, situacao}``.
        """
        logger.info(
            f"Buscando escolhas por escopo: concurso_uuid={concurso_uuid}, "
            f"ano={ano}, processo_uuids={processo_uuids}"
        )
        qs = cls._filtrar_escolhas_por_escopo(
            Escolha.objects.all(),
            concurso_uuid=concurso_uuid,
            ano=ano,
            processo_uuids=processo_uuids or None,
        )
        return list(
            qs.exclude(candidato_uuid__isnull=True).values(
                "candidato_uuid", "situacao"
            )
        )

    @classmethod
    def agregar_escolhas_por_dre(
        cls,
        *,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> list[dict[str, Any]]:
        """Agrega contagem de escolhas realizadas por DRE.

        Returns:
            Lista com ``dre_uuid``, ``nome`` e ``escolhas``.
        """
        logger.info(
            f"Agregando escolhas por DRE: concurso_uuid={concurso_uuid}, "
            f"ano={ano}, processo_uuids={processo_uuids}"
        )
        qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        qs = cls._filtrar_escolhas_por_escopo(
            qs,
            concurso_uuid=concurso_uuid,
            ano=ano,
            processo_uuids=processo_uuids or None,
        )
        return list(
            qs.values(
                dre_uuid=F("vaga_escola__escola__dre__uuid"),
                nome=F("vaga_escola__escola__dre__nome"),
            ).annotate(escolhas=Count("uuid"))
        )

    @classmethod
    def agregar_escolhas_por_concurso_dre_cargo(
        cls,
        *,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> list[dict[str, Any]]:
        """Agrega escolhas realizadas por concurso, DRE e cargo.

        Returns:
            Lista com concurso, DRE, cargo e contagens.
        """
        logger.info(
            f"Agregando escolhas por concurso/DRE/cargo: "
            f"concurso_uuid={concurso_uuid}, anos={anos}, "
            f"processo_uuids={processo_uuids}"
        )
        qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        if concurso_uuid:
            qs = qs.filter(concurso_uuid=concurso_uuid)
        if processo_uuids:
            qs = qs.filter(
                vaga_escola__lote__processo_uuid__in=processo_uuids
            )
        elif anos:
            qs = qs.filter(criado_em__year__in=anos)

        rows = list(
            qs.values(
                "concurso_uuid",
                dre_uuid=F("vaga_escola__escola__dre__uuid"),
                nome=F("vaga_escola__escola__dre__nome"),
                codigo_cargo=F("vaga_escola__cargo_codigo"),
                cargo_descricao=F("vaga_escola__cargo_descricao"),
            ).annotate(
                escolhas=Count("uuid"),
                ultima_escolha_em=Max("criado_em"),
            )
        )
        for row in rows:
            row["ultima_escolha_em"] = cls._serializar_datetime(
                row["ultima_escolha_em"]
            )
        return rows

    @classmethod
    def obter_ultima_escolha_em(
        cls,
        *,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> str | None:
        """Retorna a data ISO da última escolha realizada no escopo."""
        logger.info(
            f"Obtendo data da última escolha: concurso_uuid={concurso_uuid}, "
            f"anos={anos}, processo_uuids={processo_uuids}"
        )
        qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        if concurso_uuid:
            qs = qs.filter(concurso_uuid=concurso_uuid)
        if processo_uuids:
            qs = qs.filter(
                vaga_escola__lote__processo_uuid__in=processo_uuids
            )
        elif anos:
            qs = qs.filter(criado_em__year__in=anos)

        ultima = qs.aggregate(ultima=Max("criado_em"))["ultima"]
        return cls._serializar_datetime(ultima)
