"""Módulo views/escolha."""

from __future__ import annotations

import logging
from typing import Any

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from escolhas.middleware import get_correlation_id

from ..choices import SituacaoChoices, TipoVagaChoices
from ..models import Escolha, VagasEscolas
from ..serializers import (
    EscolhaListSerializer,
    EscolhaReconvocacaoSerializer,
    EscolhaSelectSerializer,
    EscolhaSerializer,
    EscolhasProdamImportacaoSerializer,
)
from ..services import CandidatoAPIService, ConcursoAPIService
from ..utils import CustomPagination

logger = logging.getLogger(__name__)


class EscolhaViewSet(viewsets.ModelViewSet):
    """Define EscolhaViewSet."""

    queryset = Escolha.objects.all()
    serializer_class = EscolhaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "candidato_uuid": ["exact"],
        "concurso_uuid": ["exact"],
        "situacao": ["exact", "in"],
        "vaga_escola__cargo_codigo": ["exact"],
        "vaga_escola__lote__processo_uuid": ["exact"],
    }
    search_fields = ["situacao", "tipo_vaga"]
    ordering_fields = ["criado_em"]
    ordering = ["-criado_em"]
    pagination_class = CustomPagination

    def get_queryset(self) -> Any:
        """Executa get queryset.

        Args:
            self: Instância do objeto.

        Returns:
            Valor calculado para o campo ou propriedade.

        Raises:
            Nenhuma exceção específica documentada.
        """
        qs = Escolha.objects.all()
        if self.action in ["list", "retrieve", "busca"]:
            qs = qs.select_related(
                "vaga_escola",
                "vaga_escola__escola",
                "vaga_escola__escola__dre",
            ).prefetch_related("historico")
        return qs

    def get_serializer_class(self) -> Any:
        """Executa get serializer class.

        Args:
            self: Instância do objeto.

        Returns:
            Valor calculado para o campo ou propriedade.

        Raises:
            Nenhuma exceção específica documentada.
        """
        if self.action in ["list", "busca"]:
            return EscolhaListSerializer
        if self.action == "select":
            return EscolhaSelectSerializer
        if self.action == "reconvocacao":
            return EscolhaReconvocacaoSerializer
        return super().get_serializer_class()

    def paginate_queryset(self, queryset: Any) -> Any:
        """Executa paginate queryset.

        Args:
            self: Instância do objeto.
            queryset: Parâmetro queryset da operação.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        if "no_page" in self.request.query_params:
            return None
        return super().paginate_queryset(queryset)

    def get_serializer(self, *args: Any, **kwargs: Any) -> Any:
        """Executa get serializer.

        Args:
            self: Instância do objeto.
            *args: Argumentos posicionais variáveis.
            **kwargs: Argumentos nomeados variáveis.

        Returns:
            Valor calculado para o campo ou propriedade.

        Raises:
            Nenhuma exceção específica documentada.
        """
        serializer_class = self.get_serializer_class()
        fields = self.request.query_params.get("fields")
        if fields:
            kwargs["fields"] = fields.split(",")
        return serializer_class(*args, **kwargs)

    @action(methods=["post"], detail=False, url_path="busca")
    def busca(self, request: Any) -> Any:
        """Executa busca.

        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        logger.info(
            "Buscando escolhas por candidato_uuid",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "user": request.user,
                "data": request.data,
            },
        )
        candidato_ids = request.data.get("candidato_uuid", [])
        if not isinstance(candidato_ids, list):
            return Response(
                {"detail": "candidato_uuid deve ser uma lista de UUIDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = (
            self.get_queryset()
            .select_related(
                "vaga_escola",
                "vaga_escola__escola",
                "vaga_escola__escola__dre",
            )
            .filter(candidato_uuid__in=candidato_ids)
        )
        concurso_uuid = request.data.get("concurso_uuid")
        if concurso_uuid:
            queryset = queryset.filter(concurso_uuid=concurso_uuid)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="reconvocacao")
    def reconvocacao(self, request: Any) -> Any:
        """Endpoint para buscar escolhas com situação de reconvocação.

        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        logger.info(
            "Buscando escolhas com situação de reconvocação",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "user": request.user,
            },
        )
        queryset = self.get_queryset().filter(
            situacao=SituacaoChoices.RECONVOCACAO
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False, url_path="buscar-candidatos")
    def buscar_candidatos(self, request: Any) -> Any:
        """Busca candidatos no MS-Candidatos por nome, CPF, RG ou registro.

        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        logger.info(
            "Buscando candidatos",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "user": request.user,
            },
        )
        nome = request.query_params.get("nome", "").strip()
        cpf = request.query_params.get("cpf", "").strip()
        rg = request.query_params.get("rg", "").strip()
        registro_funcional = request.query_params.get(
            "registro_funcional", ""
        ).strip()
        if not any([nome, cpf, rg, registro_funcional]):
            return Response(
                {
                    "detail": (
                        "Informe pelo menos um parâmetro: nome, cpf, rg "
                        "ou registro_funcional."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        candidatos = CandidatoAPIService().buscar_candidatos(
            nome=nome or None,
            cpf=cpf or None,
            rg=rg or None,
            registro_funcional=registro_funcional or None,
        )
        if candidatos is None:
            return Response(
                {"detail": "Erro ao consultar serviço de candidatos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        codigos_cargo = set()
        for item in candidatos:
            for cc in item.get("concursos") or []:
                cod = cc.get("codigo_cargo")
                if cod is not None and str(cod).strip():
                    codigos_cargo.add(str(cod).strip())
        cargos_map = (
            ConcursoAPIService.get_cargos_por_codigos(list(codigos_cargo))
            if codigos_cargo
            else {}
        )
        for item in candidatos:
            for cc in item.get("concursos") or []:
                cod = cc.get("codigo_cargo")
                if cod is not None and str(cod).strip():
                    nome_cargo = cargos_map.get(str(cod).strip())
                    if nome_cargo:
                        cc["descricao_cargo"] = nome_cargo
        logger.info(
            "Candidatos encontrados",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "params": request.query_params,
                "user": request.user,
            },
        )
        return Response(candidatos)

    @action(methods=["get"], detail=False, url_path="agrupar-por-cargo")
    def agrupar_por_cargo(self, request: Any) -> Any:
        """Agrupa escolhas por cargo e retorna totais por vaga.

        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        logger.info(
            "Agrupando escolhas por cargo",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "user": request.user,
            },
        )
        qs = (
            self.get_queryset()
            .filter(situacao=SituacaoChoices.ESCOLHA)
            .values("vaga_escola__cargo_codigo")
            .annotate(total=Count("uuid"))
            .order_by("vaga_escola__cargo_codigo")
        )
        data = {
            str(item["vaga_escola__cargo_codigo"]): int(item["total"] or 0)
            for item in qs
        }
        logger.info(
            "Agrupando escolhas por cargo - Resultado",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "user": request.user,
                "data": data,
            },
        )
        return Response(data)

    @action(methods=["post"], detail=False, url_path="importacao-prodam")
    def importacao_prodam(self, request: Any) -> Any:
        """Endpoint para receber dados de escolhas.

        Args:
            self: Instância do objeto.
            request: Requisição HTTP recebida.

        Returns:
            Resultado da operação.

        Raises:
            Nenhuma exceção específica documentada.
        """
        logger.info(
            "Iniciando importação de escolhas da Prodam",
            extra={
                "correlation_id": get_correlation_id(),
                "method": request.method,
                "path": request.path,
                "data": request.data,
                "user": request.user,
            },
        )
        serializer = EscolhasProdamImportacaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cpfs = [
            escolha["cpf"] for escolha in serializer.validated_data["escolhas"]
        ]
        processo_uuid = serializer.validated_data["processo_uuid"]
        candidatos = CandidatoAPIService().buscar_candidatos_por_cpfs(
            cpfs, processo_uuid
        )
        escolhas = serializer.validated_data["escolhas"]
        concurso_uuid = serializer.validated_data["concurso_uuid"]
        codigos_eol = list(
            set(
                [
                    escolha["codigo_eol"].zfill(6)
                    for escolha in escolhas
                    if escolha.get("codigo_eol")
                ]
            )
        )
        codigos_cargo = list(
            set(
                [
                    int(escolha["codigo_cargo"])
                    for escolha in escolhas
                    if escolha.get("codigo_cargo")
                ]
            )
        )
        candidatos_dict = {}
        if candidatos:
            for candidato in candidatos:
                cpf_candidato = candidato.get("cpf")  # type: ignore[attr-defined]
                if cpf_candidato:
                    candidatos_dict[cpf_candidato] = candidato.get("uuid")  # type: ignore[attr-defined]
        vagas_escolas_dict = {}
        if codigos_eol and codigos_cargo:
            try:
                vagas_escolas = VagasEscolas.objects.filter(
                    escola__codigo_eol__in=codigos_eol,
                    cargo_codigo__in=codigos_cargo,
                ).select_related("escola")
                for vaga_escola in vagas_escolas:
                    codigo_eol = vaga_escola.escola.codigo_eol
                    codigo_cargo = str(vaga_escola.cargo_codigo)
                    chave = (codigo_eol, codigo_cargo)
                    vagas_escolas_dict[chave] = vaga_escola
                logger.info(
                    "Vagas encontradas: %s (EOL=%s, cargos=%s)",
                    len(vagas_escolas_dict),
                    len(codigos_eol),
                    len(codigos_cargo),
                )
            except Exception as exc:
                logger.error(f"Erro ao buscar vagas_escolas: {exc}")
        escolhas_criadas = []
        erros = []
        for idx, escolha_data in enumerate(escolhas):
            try:
                cpf_escolha = escolha_data.get("cpf")
                candidato_uuid = candidatos_dict.get(cpf_escolha)
                if not candidato_uuid:
                    erros.append(
                        {
                            "index": idx,
                            "cpf": cpf_escolha,
                            "erro": "Candidato não encontrado",
                        }
                    )
                    continue
                codigo_eol = escolha_data.get("codigo_eol")
                codigo_cargo = escolha_data.get("codigo_cargo")
                vaga_escola = None  # type: ignore[assignment]
                if codigo_eol and codigo_cargo:
                    codigo_eol_normalizado = str(codigo_eol).zfill(6)
                    codigo_cargo_str = str(codigo_cargo)
                    chave = (codigo_eol_normalizado, codigo_cargo_str)
                    vaga_escola = vagas_escolas_dict.get(chave)  # type: ignore[assignment]
                situacao_map = {
                    "ESCOLHA": SituacaoChoices.ESCOLHA,
                    "NAO-ESCOLHA": SituacaoChoices.NAO_ESCOLHA,
                    "RECONVOCACAO": SituacaoChoices.RECONVOCACAO,
                    "PENDENTE": SituacaoChoices.NAO_ESCOLHA,
                }
                situacao = situacao_map.get(
                    escolha_data.get("situacao", "").upper(),
                    SituacaoChoices.NAO_ESCOLHA,
                )
                tipo_vaga = None
                tipo_vaga_raw = escolha_data.get("tipo_vaga")
                if tipo_vaga_raw:
                    tipo_vaga_map = {
                        "P": TipoVagaChoices.PRECARIA,
                        "D": TipoVagaChoices.DEFINITIVA,
                    }
                    tipo_vaga = tipo_vaga_map.get(str(tipo_vaga_raw).upper())
                escolha_existente = Escolha.objects.filter(
                    candidato_uuid=candidato_uuid, concurso_uuid=concurso_uuid
                ).first()
                if escolha_existente:
                    logger.warning(
                        "Escolha duplicada na importação (idx=%s, cpf=%s): %s",
                        idx,
                        cpf_escolha,
                        escolha_existente.uuid,
                    )
                    continue
                nova_escolha = Escolha.objects.create(
                    candidato_uuid=candidato_uuid,
                    concurso_uuid=concurso_uuid,
                    situacao=situacao,
                    tipo_vaga=tipo_vaga,
                    vaga_escola=vaga_escola,
                )
                escolhas_criadas.append(
                    {
                        "uuid": str(nova_escolha.uuid),
                        "candidato_uuid": str(candidato_uuid),
                        "situacao": nova_escolha.situacao,
                    }
                )
            except Exception as exc:
                logger.error(
                    f"Erro ao criar escolha {idx}: {exc}", exc_info=True
                )
                erros.append(
                    {
                        "index": idx,
                        "cpf": escolha_data.get("cpf", "N/A"),
                        "erro": str(exc),
                    }
                )
        response_data = {
            "escolhas_criadas": len(escolhas_criadas),
            "escolhas": escolhas_criadas,
        }
        if erros:
            logger.info(
                "Erros ao criar escolhas",
                extra={"correlation_id": get_correlation_id(), "erros": erros},
            )
            response_data["erros"] = erros
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        logger.info(
            "Escolhas criadas",
            extra={
                "correlation_id": get_correlation_id(),
                "escolhas_criadas": len(escolhas_criadas),
                "escolhas": escolhas_criadas[:10],
            },
        )
        return Response(response_data, status=status.HTTP_201_CREATED)
