"""Repositório de acesso a dados de vagas de escolas e lotes.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.db import models
from django.db.models import F, QuerySet, Sum
from django.db.models.functions import Greatest

from vagas_escolas.models import VagasEscolas, VagasEscolasLote

logger = logging.getLogger(__name__)


class VagasEscolasRepository:
    """Acesso aos dados de vagas de escolas e lotes."""

    @classmethod
    def obter_lote_mais_recente_por_processo(
        cls, processo_uuid: str | UUID
    ) -> VagasEscolasLote | None:
        """Retorna o lote mais recente do processo."""
        logger.info(
            f"Buscando lote mais recente do processo: {processo_uuid}"
        )
        return (
            VagasEscolasLote.objects.filter(processo_uuid=processo_uuid)
            .order_by("-criado_em")
            .first()
        )

    @classmethod
    def criar_lote(
        cls,
        *,
        processo_uuid: str | UUID,
        processo_nome: str = "",
        concurso_uuid: str | UUID | None = None,
    ) -> VagasEscolasLote:
        """Cria um lote de vagas do processo."""
        logger.info(
            f"Criando lote de vagas: processo_uuid={processo_uuid}, "
            f"concurso_uuid={concurso_uuid}"
        )
        return VagasEscolasLote.objects.create(
            processo_uuid=processo_uuid,
            processo_nome=processo_nome,
            concurso_uuid=concurso_uuid,
        )

    @classmethod
    def excluir_lotes_por_processo(cls, processo_uuid: str | UUID) -> int:
        """Exclui lotes (e vagas em cascata) do processo.

        Returns:
            Quantidade de lotes excluídos.
        """
        logger.info(f"Excluindo lotes do processo: {processo_uuid}")
        deleted, _ = VagasEscolasLote.objects.filter(
            processo_uuid=processo_uuid
        ).delete()
        return deleted

    @classmethod
    def criar_vaga(cls, **dados: Any) -> VagasEscolas:
        """Persiste uma vaga de escola."""
        logger.info(
            f"Criando vaga de escola: cargo_codigo={dados.get('cargo_codigo')}, "
            f"escola={dados.get('escola')}"
        )
        return VagasEscolas.objects.create(**dados)

    @classmethod
    def buscar_por_uuids(
        cls, uuids: list[str | UUID]
    ) -> list[VagasEscolas]:
        """Busca vagas pelos UUIDs (modelos para atualização)."""
        logger.info(f"Buscando vagas pelos UUIDs: {uuids}")
        return list(VagasEscolas.objects.filter(uuid__in=uuids))

    @classmethod
    def obter_por_uuid(cls, vaga_uuid: str | UUID) -> VagasEscolas:
        """Busca vaga pelo UUID (modelo para validação/persistência).

        Raises:
            VagasEscolas.DoesNotExist: Quando não encontrada.
        """
        logger.info(f"Buscando vaga pelo UUID: {vaga_uuid}")
        return VagasEscolas.objects.get(uuid=vaga_uuid)

    @classmethod
    def listar_por_cargo_e_eols(
        cls,
        *,
        cargo_codigo: str | int | None = None,
        eols: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Lista vagas filtradas por cargo e/ou EOLs, serializadas."""
        logger.info(
            f"Listando vagas por cargo_codigo={cargo_codigo} e eols={eols}"
        )
        qs = VagasEscolas.objects.select_related("escola")
        if cargo_codigo:
            qs = qs.filter(cargo_codigo=cargo_codigo)
        if eols:
            qs = qs.filter(escola__codigo_eol__in=eols)
        return cls.montar_lista_resposta(list(qs))

    @classmethod
    def listar_por_eols_e_cargos(
        cls, eols: list[str], cargos: list[int]
    ) -> list[VagasEscolas]:
        """Lista vagas por EOLs e cargos (modelos para importação Prodam)."""
        logger.info(f"Listando vagas por eols={eols} e cargos={cargos}")
        return list(
            VagasEscolas.objects.filter(
                escola__codigo_eol__in=eols, cargo_codigo__in=cargos
            ).select_related("escola")
        )

    @classmethod
    def montar_listagem(
        cls, qs: QuerySet[VagasEscolas]
    ) -> dict[str, Any]:
        """Monta listagem com vagas checadas, totais e DREs.

        Args:
            qs: QuerySet já filtrado pela view (processo, cargo, etc.).

        Returns:
            Dicionário com ``vagas``, totais e ``dres``.
        """
        logger.info("Montando listagem de vagas checadas com totais e DREs")
        qs = qs.filter(esta_checada=True)
        ha_utilizadas = qs.filter(
            models.Q(vagas_precarias_utilizadas__isnull=False)
            | models.Q(vagas_definitivas_utilizadas__isnull=False)
        ).exists()
        if ha_utilizadas:
            totais = qs.aggregate(
                vagas_precarias=Sum("vagas_precarias_utilizadas"),
                vagas_definitivas=Sum("vagas_definitivas_utilizadas"),
            )
        else:
            totais = qs.aggregate(
                vagas_precarias=Sum("vagas_precarias"),
                vagas_definitivas=Sum("vagas_definitivas"),
            )
        dres = list(
            qs.values(
                "escola__dre__codigo",
                "escola__dre__nome",
                "escola__dre__uuid",
            )
            .distinct()
            .order_by("escola__dre__codigo")
        )
        dres_fmt = [
            {
                "codigo": d["escola__dre__codigo"],
                "nome": d["escola__dre__nome"],
                "uuid": d["escola__dre__uuid"],
            }
            for d in dres
        ]
        return {
            "vagas": cls.montar_lista_resposta(qs),
            "total_vagas": int(totais["vagas_precarias"] or 0)
            + int(totais["vagas_definitivas"] or 0),
            "total_vagas_precarias": int(totais["vagas_precarias"] or 0),
            "total_vagas_definitivas": int(totais["vagas_definitivas"] or 0),
            "dres": dres_fmt,
        }

    @classmethod
    def decrementar_definitivas_restantes(cls, pk: Any) -> int:
        """Decrementa vagas definitivas restantes (mínimo 0)."""
        logger.info(
            f"Decrementando vagas definitivas restantes da vaga pk={pk}"
        )
        return VagasEscolas.objects.filter(pk=pk).update(
            vagas_definitivas_restantes=Greatest(
                0, F("vagas_definitivas_restantes") - 1
            )
        )

    @classmethod
    def decrementar_precarias_restantes(cls, pk: Any) -> int:
        """Decrementa vagas precárias restantes (mínimo 0)."""
        logger.info(
            f"Decrementando vagas precárias restantes da vaga pk={pk}"
        )
        return VagasEscolas.objects.filter(pk=pk).update(
            vagas_precarias_restantes=Greatest(
                0, F("vagas_precarias_restantes") - 1
            )
        )

    @classmethod
    def agregar_vagas_por_dre(
        cls, processo_uuids: list[UUID | str] | None = None
    ) -> list[dict[str, Any]]:
        """Agrega total de vagas ofertadas por DRE."""
        logger.info(
            f"Agregando vagas por DRE: processo_uuids={processo_uuids}"
        )
        qs = VagasEscolas.objects.all()
        if processo_uuids:
            qs = qs.filter(lote__processo_uuid__in=processo_uuids)
        return list(
            qs.values(
                dre_uuid=F("escola__dre__uuid"),
                nome=F("escola__dre__nome"),
            ).annotate(vagas=Sum(F("vagas_definitivas") + F("vagas_precarias")))
        )

    @classmethod
    def agregar_vagas_por_concurso_dre_cargo(
        cls, processo_uuids: list[UUID | str] | None = None
    ) -> list[dict[str, Any]]:
        """Agrega vagas por concurso, DRE e cargo (via lote.concurso_uuid)."""
        logger.info(
            f"Agregando vagas por concurso/DRE/cargo: "
            f"processo_uuids={processo_uuids}"
        )
        qs = VagasEscolas.objects.filter(lote__concurso_uuid__isnull=False)
        if processo_uuids:
            qs = qs.filter(lote__processo_uuid__in=processo_uuids)
        return list(
            qs.values(
                "cargo_codigo",
                "cargo_descricao",
                concurso=F("lote__concurso_uuid"),
                dre_uuid=F("escola__dre__uuid"),
                nome=F("escola__dre__nome"),
            ).annotate(vagas=Sum(F("vagas_definitivas") + F("vagas_precarias")))
        )

    @staticmethod
    def montar_lista_resposta(
        vagas: QuerySet[VagasEscolas] | list[VagasEscolas],
    ) -> list[dict[str, Any]]:
        """Serializa vagas para resposta da API."""
        from vagas_escolas.serializers import VagasEscolasSerializer

        return VagasEscolasSerializer(vagas, many=True).data
