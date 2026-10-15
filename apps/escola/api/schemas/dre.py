"""Documentação OpenAPI das operações de DREs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema

from core.openapi import (
    AVISO_ROTA_HERDADA,
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
    RESPOSTA_PAGINA_INEXISTENTE,
    exemplo_pagina,
    exemplos_requisicao,
    parametro_busca,
    parametro_ordenacao,
    parametro_uuid,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from escola.models import Dre
from escola.serializers import DrePaginadaSerializer, DreSerializer

TAG_DRES = "DREs"

UUID_DRE_EXEMPLO = "2c6f1a3e-8b4d-4f7a-9e21-5d0c3b7a6e18"
CODIGO_DRE_EXEMPLO = "108100"
NOME_DRE_EXEMPLO = "DIRETORIA REGIONAL DE EDUCACAO BUTANTA"
SIGLA_DRE_EXEMPLO = "DRE - BT"

EXEMPLO_DADOS_DRE = {
    "codigo": CODIGO_DRE_EXEMPLO,
    "nome": NOME_DRE_EXEMPLO,
    "sigla": SIGLA_DRE_EXEMPLO,
}

EXEMPLO_DRE = {"uuid": UUID_DRE_EXEMPLO, **EXEMPLO_DADOS_DRE}

ERRO_SIGLA_LONGA = {
    "sigla": [
        "Certifique-se de que este campo não tenha mais de 50 caracteres."
    ]
}

PARAMETRO_UUID = parametro_uuid("UUID da DRE.")

PARAMETROS_LISTAGEM = [
    parametro_busca("Busca por trecho do nome, da sigla ou do código."),
    parametro_ordenacao(["criado_em", "nome"], "-criado_em"),
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
]

RESPOSTA_DRE = resposta(DreSerializer, "DRE.", {"DRE": EXEMPLO_DRE})

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(Dre)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos.",
    {
        "Campos ausentes": {
            "codigo": ["Este campo é obrigatório."],
            "nome": ["Este campo é obrigatório."],
            "sigla": ["Este campo é obrigatório."],
        },
        "Sigla longa demais": ERRO_SIGLA_LONGA,
    },
)

OPERACOES_DRES = {
    "list": extend_schema(
        operation_id="listar_dres",
        summary="Listar DREs",
        description=(
            "Retorna as DREs em páginas, da cadastrada mais recentemente "
            "para a mais antiga."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    DrePaginadaSerializer,
                    "Página de DREs.",
                    {"Página": exemplo_pagina([EXEMPLO_DRE])},
                ),
                404: RESPOSTA_PAGINA_INEXISTENTE,
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_dre",
        summary="Criar DRE",
        description=(
            "Cria uma DRE. O serviço não impede duas DREs com o mesmo "
            "código.\n\n"
            f"{AVISO_ROTA_HERDADA} As DREs são carregadas da integração "
            "com a SME."
        ),
        request=DreSerializer,
        examples=exemplos_requisicao({"Nova DRE": EXEMPLO_DADOS_DRE}),
        responses=respostas(
            {
                201: resposta(
                    DreSerializer, "DRE criada.", {"DRE": EXEMPLO_DRE}
                ),
                400: RESPOSTA_DADOS_INVALIDOS,
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_dre",
        summary="Detalhar DRE",
        description=f"Retorna uma DRE pelo UUID.\n\n{AVISO_ROTA_HERDADA}",
        parameters=[PARAMETRO_UUID],
        responses=respostas({200: RESPOSTA_DRE, 404: RESPOSTA_NAO_ENCONTRADO}),
    ),
    "update": extend_schema(
        operation_id="atualizar_dre",
        summary="Atualizar DRE",
        description=(
            "Substitui os dados da DRE. Os três campos são obrigatórios."
            f"\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=DreSerializer,
        examples=exemplos_requisicao({"Dados da DRE": EXEMPLO_DADOS_DRE}),
        responses=respostas(
            {
                200: RESPOSTA_DRE,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_dre",
        summary="Atualizar DRE parcialmente",
        description=(
            f"Altera apenas os campos enviados.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=DreSerializer,
        examples=exemplos_requisicao(
            {"Corrigir a sigla": {"sigla": SIGLA_DRE_EXEMPLO}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_DRE,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {"Sigla longa demais": ERRO_SIGLA_LONGA},
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_dre",
        summary="Excluir DRE",
        description=(
            "Exclui a DRE definitivamente, junto com as escolas dela e as "
            "vagas dessas escolas. As escolhas feitas nessas vagas "
            "continuam, mas ficam sem vaga.\n\n"
            f"{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "DRE excluída."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
}
