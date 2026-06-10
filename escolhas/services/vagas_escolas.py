"""Módulo services/vagas_escolas."""

import logging
from typing import Any

from django.db import transaction
from rest_framework import status

from ..models import Escola, Parametrizacao, VagasEscolas, VagasEscolasLote
from ..serializers import VagasEscolasCreateSerializer
from .exceptions import TipoUEDesabilitadoException

logger = logging.getLogger(__name__)


def criar_vagas_em_lote(
    vagas_data: list[dict[str, Any]], lote: VagasEscolasLote
) -> tuple[list[VagasEscolas], list[dict[str, Any]]]:
    """Cria vagas em lote.

    Args:
        vagas_data: Vagas data utilizado na operação.
        lote: Lote de concurso usado no teste.

    Returns:
        Tupla com os objetos criados ou atualizados.
    """
    errors = []
    created_vagas = []

    for i, vaga_data in enumerate(vagas_data):
        try:
            codigo_eol = vaga_data.pop("codigo_eol")
            codigo_eol = codigo_eol.zfill(6)
            try:
                escola = Escola.objects.get(codigo_eol=codigo_eol)
            except Escola.DoesNotExist:
                error_msg = f"Escola com código EOL '{codigo_eol}' não encontrada na vaga {i+1}"  # noqa: E501
                logger.error(error_msg)
                errors.append(
                    {
                        "vaga_index": i + 1,
                        "codigo_eol": codigo_eol,
                        "error": error_msg,
                    }
                )
                continue
            vaga = VagasEscolas.objects.create(
                escola=escola,
                lote=lote,
                **vaga_data,
                vagas_definitivas_restantes=vaga_data.get(
                    "vagas_definitivas", 0
                ),
                vagas_precarias_restantes=vaga_data.get("vagas_precarias", 0),
            )
            created_vagas.append(vaga)
        except Exception as e:
            error_msg = f"Erro ao criar vaga {i+1}: {str(e)}"
            logger.error(error_msg)
            errors.append({"vaga_index": i + 1, "error": error_msg})
            continue

    return created_vagas, errors


def processar_criacao_vagas_lote(
    request_data: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Processa criacao vagas lote.

    Args:
        request_data: Request data utilizado na operação.

    Returns:
        Tupla com os objetos criados ou atualizados.

    Raises:
        TipoUEDesabilitadoException: Se ocorrer erro nesta operação.
    """
    serializer = VagasEscolasCreateSerializer(data=request_data)

    if not serializer.is_valid():
        return {"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
    processo_uuid = serializer.validated_data["processo_uuid"]
    processo_nome = serializer.validated_data.get("processo_nome", "")
    vagas_data = serializer.validated_data["vagas"]

    # Validação: impedir criação de vagas para escolas cujo tipo_ue está desabilitado em Parametrizacao (usar=False)  # noqa: E501
    tipos_bloqueados = set(
        Parametrizacao.objects.filter(usar=False).values_list(
            "tipo_ue", flat=True
        )
    )
    if tipos_bloqueados:
        for item in vagas_data:
            codigo_eol = str(item.get("codigo_eol", "")).zfill(6)
            if not codigo_eol:
                # Será tratado posteriormente; aqui só validamos tipos bloqueados  # noqa: E501
                continue
            try:
                escola = Escola.objects.only("tipo_ue").get(
                    codigo_eol=codigo_eol
                )
            except Escola.DoesNotExist:
                # Deixa o fluxo normal tratar escola inexistente
                continue
            if escola.tipo_ue in tipos_bloqueados:
                raise TipoUEDesabilitadoException(
                    f"Tipo de unidade '{escola.tipo_ue}' da escola EOL {codigo_eol} está desabilitado."  # noqa: E501
                )

    with transaction.atomic():
        lote = VagasEscolasLote.objects.create(
            processo_uuid=processo_uuid, processo_nome=processo_nome
        )
        created_vagas, errors = criar_vagas_em_lote(vagas_data, lote)

    response_data = {
        "mensagem": f"{len(created_vagas)} vagas criadas com sucesso",
        "vagas_criadas": len(created_vagas),
        "total_processadas": len(vagas_data),
        "lote_uuid": str(lote.uuid),
        "processo_uuid": str(processo_uuid),
    }

    if errors:
        response_data["erros"] = errors
        response_data["vagas_com_erro"] = len(errors)

    if not created_vagas and errors:
        status_code = status.HTTP_400_BAD_REQUEST
    elif errors:
        status_code = status.HTTP_207_MULTI_STATUS  # type: ignore[assignment]
    else:
        status_code = status.HTTP_201_CREATED  # type: ignore[assignment]

    return response_data, status_code


def atualizar_vagas_utilizadas_por_processo(
    vagas: list[dict[str, Any]],
) -> dict[str, Any]:
    """Atualiza vagas utilizadas por processo.

    Args:
        vagas: Vagas utilizado na operação.

    Returns:
        Dicionário com os dados retornados pela operação.
    """
    from ..models import VagasEscolas  # import local para evitar ciclos

    uuid_to_item = {str(item["uuid"]): item for item in vagas}
    vagas_escolas = VagasEscolas.objects.filter(
        uuid__in=list(uuid_to_item.keys())
    )

    encontrados = set()
    atualizados = []
    for vaga in vagas_escolas:
        encontrados.add(str(vaga.uuid))
        item = uuid_to_item.get(str(vaga.uuid))
        updates = {}
        if "foi_utilizada" in item:  # type: ignore[operator]
            vaga.foi_utilizada = item["foi_utilizada"]  # type: ignore[index]
            vaga.esta_checada = bool(vaga.foi_utilizada)
            updates["foi_utilizada"] = item["foi_utilizada"]  # type: ignore[index]
            updates["esta_checada"] = bool(vaga.foi_utilizada)
        if "vagas_precarias_utilizadas" in item:  # type: ignore[operator]
            vaga.vagas_precarias_utilizadas = item[  # type: ignore[index]
                "vagas_precarias_utilizadas"
            ]
            updates["vagas_precarias_utilizadas"] = item[  # type: ignore[index]
                "vagas_precarias_utilizadas"
            ]
        if "vagas_definitivas_utilizadas" in item:  # type: ignore[operator]
            vaga.vagas_definitivas_utilizadas = item[  # type: ignore[index]
                "vagas_definitivas_utilizadas"
            ]
            updates["vagas_definitivas_utilizadas"] = item[  # type: ignore[index]
                "vagas_definitivas_utilizadas"
            ]
        if updates:
            vaga.save(update_fields=list(updates.keys()))
            atualizados.append(str(vaga.uuid))

    nao_encontrados = [uid for uid in uuid_to_item if uid not in encontrados]

    return {
        "atualizados": atualizados,
        "nao_encontrados": nao_encontrados,
        "total": len(atualizados),
    }


def adicionar_vagas_ao_lote_por_processo(
    request_data: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Adiciona vagas a um lote existente pelo processo_uuid.

    Args:
        request_data: Request data utilizado na operação.

    Returns:
        Tupla com os objetos criados ou atualizados.
    """
    serializer = VagasEscolasCreateSerializer(data=request_data)
    if not serializer.is_valid():
        return {"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST

    processo_uuid = serializer.validated_data["processo_uuid"]
    serializer.validated_data.get("processo_nome", "")
    vagas_data = serializer.validated_data["vagas"]

    lote = (
        VagasEscolasLote.objects.filter(processo_uuid=processo_uuid)
        .order_by("-criado_em")
        .first()
    )
    if not lote:
        return {
            "detail": "Lote não encontrado para o processo informado"
        }, status.HTTP_404_NOT_FOUND

    criadas, erros = criar_vagas_em_lote(vagas_data, lote)

    resposta = {
        "mensagem": f"{len(criadas)} vagas adicionadas ao lote",
        "vagas_criadas": len(criadas),
        "total_processadas": len(vagas_data),
        "lote_uuid": str(lote.uuid),
        "processo_uuid": str(processo_uuid),
    }
    if erros:
        resposta["erros"] = erros
        resposta["vagas_com_erro"] = len(erros)
        return resposta, status.HTTP_207_MULTI_STATUS
    return resposta, status.HTTP_201_CREATED
