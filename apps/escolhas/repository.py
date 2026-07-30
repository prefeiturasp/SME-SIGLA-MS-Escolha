"""Repositório de acesso a dados de escolhas.

As consultas de leitura retornam dados já serializados (dict / list[dict]),
não QuerySets do Django, quando aplicável à resposta da API.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import Count, F, Max, Q, QuerySet

from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha, HistoricoEscolha
from vagas_escolas.repository import VagasEscolasRepository


class EscolhaRepository:
    """Acesso aos dados de escolhas e histórico."""

    @classmethod
    def obter_por_pk(cls, pk: Any) -> Escolha:
        """Busca escolha pela PK.

        Raises:
            Escolha.DoesNotExist: Quando não encontrada.
        """
        return Escolha.objects.get(pk=pk)

    @classmethod
    def obter_por_candidato_e_concurso(
        cls, candidato_uuid: Any, concurso_uuid: Any
    ) -> Escolha | None:
        """Busca a primeira escolha do candidato no concurso."""
        return Escolha.objects.filter(
            candidato_uuid=candidato_uuid, concurso_uuid=concurso_uuid
        ).first()

    @classmethod
    def criar(cls, **kwargs: Any) -> Escolha:
        """Persiste uma nova escolha."""
        return Escolha.objects.create(**kwargs)

    @classmethod
    def contar_por_cargo(cls) -> dict[str, int]:
        """Conta escolhas realizadas agrupadas por cargo."""
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
        return HistoricoEscolha.objects.create(
            escolha=escolha,
            situacao_anterior=situacao_anterior,
            situacao_nova=situacao_nova,
        )

    @staticmethod
    def montar_resposta(escolha: Escolha) -> dict[str, Any]:
        """Transforma uma escolha em dicionário de resposta."""
        from escolhas.serializers import EscolhaSerializer

        return EscolhaSerializer(escolha).data

    @classmethod
    def montar_lista_resposta(
        cls, escolhas: list[Escolha]
    ) -> list[dict[str, Any]]:
        """Transforma uma lista de escolhas em dicionários de listagem."""
        from escolhas.serializers import EscolhaListSerializer

        return EscolhaListSerializer(escolhas, many=True).data

    @classmethod
    def listar_todos(cls) -> list[dict[str, Any]]:
        """Lista todas as escolhas serializadas (mais recentes primeiro)."""
        escolhas = list(Escolha.objects.all().order_by("-criado_em"))
        return cls.montar_lista_resposta(escolhas)

    @classmethod
    def obter_por_uuid(
        cls, escolha_uuid: str | UUID
    ) -> dict[str, Any] | None:
        """Busca escolha pelo UUID e devolve resposta serializada."""
        escolha = Escolha.objects.filter(uuid=escolha_uuid).first()
        return cls.montar_resposta(escolha) if escolha else None

    @staticmethod
    def _serializar_datetime(value: Any) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @classmethod
    def _base_escolhas_com_vaga_qs(
        cls,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> QuerySet:
        qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        if concurso_uuid:
            qs = qs.filter(concurso_uuid=concurso_uuid)
        if processo_uuids:
            qs = qs.filter(vaga_escola__lote__processo_uuid__in=processo_uuids)
        elif anos:
            qs = qs.filter(criado_em__year__in=anos)
        return qs

    @classmethod
    def _filtrar_escolhas_por_escopo(
        cls,
        qs: QuerySet,
        *,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> QuerySet:
        """Restringe escolhas ao escopo do filtro de extração."""
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
    def _montar_filtros_resposta(
        cls, filtros: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return [
            {
                "ano": filtro["ano"],
                "processo_uuids": [
                    str(processo_uuid)
                    for processo_uuid in (filtro.get("processo_uuids") or [])
                ],
            }
            for filtro in sorted(filtros, key=lambda item: item["ano"])
        ]

    @classmethod
    def _obter_ultima_escolha_em(
        cls,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> str | None:
        ultima = cls._base_escolhas_com_vaga_qs(
            concurso_uuid=concurso_uuid,
            anos=anos,
            processo_uuids=processo_uuids,
        ).aggregate(ultima=Max("criado_em"))["ultima"]
        return cls._serializar_datetime(ultima)

    @classmethod
    def contar_escolhas(
        cls,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> dict[str, int]:
        """Conta escolhas por situação."""
        qs = cls._filtrar_escolhas_por_escopo(
            Escolha.objects.all(),
            concurso_uuid=concurso_uuid,
            ano=ano,
            processo_uuids=processo_uuids or None,
        )
        contagens = qs.values("situacao").annotate(total=Count("uuid"))
        por_situacao: dict[str, int] = {
            item["situacao"]: item["total"] for item in contagens
        }
        return {
            "escolha": por_situacao.get(SituacaoChoices.ESCOLHA, 0),
            "reconvocacao": por_situacao.get(SituacaoChoices.RECONVOCACAO, 0),
            "nao-escolha": por_situacao.get(SituacaoChoices.NAO_ESCOLHA, 0),
        }

    @classmethod
    def _montar_dres(
        cls,
        concurso_uuid: UUID | str | None = None,
        ano: int | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> list[dict[str, Any]]:
        """Une, por DRE, as escolhas realizadas e as vagas ofertadas."""
        escolhas_qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        escolhas_qs = cls._filtrar_escolhas_por_escopo(
            escolhas_qs,
            concurso_uuid=concurso_uuid,
            ano=ano,
            processo_uuids=processo_uuids or None,
        )
        escolhas_qs = escolhas_qs.values(
            dre_uuid=F("vaga_escola__escola__dre__uuid"),
            nome=F("vaga_escola__escola__dre__nome"),
        ).annotate(escolhas=Count("uuid"))

        vagas_qs = VagasEscolasRepository.agregar_vagas_por_dre(processo_uuids)

        dres: dict[Any, dict[str, Any]] = {}
        for item in escolhas_qs:
            dres[item["dre_uuid"]] = {
                "nome": item["nome"],
                "escolhas": item["escolhas"],
                "vagas": 0,
            }
        for item in vagas_qs:
            entrada = dres.setdefault(
                item["dre_uuid"],
                {"nome": item["nome"], "escolhas": 0, "vagas": 0},
            )
            entrada["vagas"] = item["vagas"] or 0

        return list(dres.values())

    @classmethod
    def _montar_dres_concursos(
        cls,
        concurso_uuid: UUID | str | None = None,
        anos: list[int] | None = None,
        processo_uuids: list[UUID | str] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Detalha, por concurso, as escolhas e vagas por DRE e cargo."""
        escolhas_qs = Escolha.objects.filter(
            situacao=SituacaoChoices.ESCOLHA,
            vaga_escola__isnull=False,
        )
        if concurso_uuid:
            escolhas_qs = escolhas_qs.filter(concurso_uuid=concurso_uuid)
        if processo_uuids:
            escolhas_qs = escolhas_qs.filter(
                vaga_escola__lote__processo_uuid__in=processo_uuids
            )
        elif anos:
            escolhas_qs = escolhas_qs.filter(criado_em__year__in=anos)

        contagem_qs = escolhas_qs.values(
            "concurso_uuid",
            dre_uuid=F("vaga_escola__escola__dre__uuid"),
            nome=F("vaga_escola__escola__dre__nome"),
            codigo_cargo=F("vaga_escola__cargo_codigo"),
            cargo_descricao=F("vaga_escola__cargo_descricao"),
        ).annotate(
            escolhas=Count("uuid"),
            ultima_escolha_em=Max("criado_em"),
        )

        por_concurso: dict[str, dict[tuple, dict[str, Any]]] = {}
        for item in contagem_qs:
            cuuid = str(item["concurso_uuid"])
            chave = (item["dre_uuid"], item["codigo_cargo"])
            por_concurso.setdefault(cuuid, {})[chave] = {
                "nome": item["nome"],
                "escolhas": item["escolhas"],
                "vagas": 0,
                "codigo_cargo": item["codigo_cargo"],
                "cargo_descricao": item["cargo_descricao"],
                "ultima_escolha_em": cls._serializar_datetime(
                    item["ultima_escolha_em"]
                ),
            }

        vagas_qs = VagasEscolasRepository.agregar_vagas_por_concurso_dre_cargo(
            processo_uuids
        )

        for vaga in vagas_qs:
            cuuid = str(vaga["concurso"])
            chave = (vaga["dre_uuid"], vaga["cargo_codigo"])
            linha = por_concurso.setdefault(cuuid, {}).setdefault(
                chave,
                {
                    "nome": vaga["nome"],
                    "escolhas": 0,
                    "vagas": 0,
                    "codigo_cargo": vaga["cargo_codigo"],
                    "cargo_descricao": vaga["cargo_descricao"],
                },
            )
            linha["vagas"] += vaga["vagas"] or 0

        return {
            cuuid: list(linhas.values())
            for cuuid, linhas in por_concurso.items()
        }

    @classmethod
    def montar_extracao_dados(
        cls,
        concurso_uuid: UUID | str | None = None,
        filtros: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Monta o dicionário de indicadores de escolhas."""
        resultado: dict[str, Any] = {}
        if filtros:
            filtros_ordenados = sorted(filtros, key=lambda item: item["ano"])
            if concurso_uuid:
                resultado["concurso_uuid"] = str(concurso_uuid)
            resultado["filtros"] = cls._montar_filtros_resposta(
                filtros_ordenados
            )

            processos_uniao: list = []
            for filtro in filtros_ordenados:
                ano = filtro["ano"]
                processo_uuids = filtro.get("processo_uuids") or []
                processos_uniao.extend(processo_uuids)
                dados = cls.contar_escolhas(
                    concurso_uuid, ano, processo_uuids=processo_uuids
                )
                dados["dres"] = cls._montar_dres(
                    concurso_uuid, ano, processo_uuids
                )
                resultado[str(ano)] = dados
            anos = [f["ano"] for f in filtros_ordenados]
        else:
            dados = cls.contar_escolhas(concurso_uuid, ano=None)
            dados["dres"] = cls._montar_dres(concurso_uuid)
            resultado.update(dados)
            anos = None
            processos_uniao = []

        resultado["dres_concursos"] = cls._montar_dres_concursos(
            concurso_uuid, anos, processos_uniao
        )
        resultado["ultima_escolha_em"] = cls._obter_ultima_escolha_em(
            concurso_uuid=concurso_uuid,
            anos=anos,
            processo_uuids=processos_uniao or None,
        )
        return resultado
