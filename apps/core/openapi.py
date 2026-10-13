"""Blocos compartilhados da documentação OpenAPI do microsserviço."""

from __future__ import annotations

from typing import Any

from django.db.models import Model
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    Direction,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
)

from core.serializers import (
    ErroAcessoSerializer,
    ErroDetalheSerializer,
    ErrosValidacaoSerializer,
)

TAMANHO_PAGINA_PADRAO = 10

UUID_CONCURSO_EXEMPLO = "7e6d5c4b-3a2f-4e1d-9c8b-7a6f5e4d3c2b"
UUID_PROCESSO_EXEMPLO = "c1a7e0d2-4b3f-4a6e-8d9c-0f1e2d3c4b5a"
NOME_PROCESSO_EXEMPLO = "1ª convocação — Professor de Educação Infantil"
UUID_CANDIDATO_EXEMPLO = "4f0c2b9e-6a1d-4c7b-9e35-2d8a1b7c6f04"
UUID_CANDIDATO_2_EXEMPLO = "a3d5e7f9-1b2c-4d6e-8f0a-9b8c7d6e5f41"
CODIGO_CARGO_EXEMPLO = 3859
NOME_CARGO_EXEMPLO = "PROF. DE ED. INFANTIL"

AVISO_ROTA_HERDADA = (
    "Rota herdada do CRUD genérico: hoje nenhuma tela ou serviço do SIGLA "
    "a chama."
)

EXEMPLO_TOKEN_INVALIDO = {
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid",
        }
    ],
}

EXEMPLO_USUARIO_NAO_ENCONTRADO = {
    "detail": "User not found",
    "code": "user_not_found",
}

EXEMPLO_BASIC_INVALIDO = {"detail": "Usuário ou senha inválido."}

ERRO_LISTA_ESPERADA = {
    "non_field_errors": [
        'Necessário uma lista de itens, mas recebeu tipo "dict".'
    ]
}


class ErrosValidacaoExtension(OpenApiSerializerExtension):
    """Descreve ``ErrosValidacaoSerializer`` como mapa campo → mensagens."""

    target_class = ErrosValidacaoSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema do mapa de erros de validação."""
        return {
            "type": "object",
            "description": (
                "Erros de validação. Cada chave é o nome de um campo ou "
                "filtro inválido (ou `non_field_errors`) e o valor é a "
                "lista de mensagens. Em campos que são listas de objetos, "
                "o valor é uma lista com um objeto de erros por item "
                "enviado. Em listas de valores simples, o valor é um "
                "objeto que liga a posição do item inválido às suas "
                "mensagens."
            ),
            "additionalProperties": {
                "oneOf": [
                    {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"type": "string"},
                                {
                                    "type": "object",
                                    "additionalProperties": True,
                                },
                            ]
                        },
                    },
                    {"type": "object", "additionalProperties": True},
                ]
            },
        }


ERROS_VALIDACAO_EM_LOTE = PolymorphicProxySerializer(
    component_name="ErrosValidacaoEmLote",
    serializers=[
        ErrosValidacaoSerializer(many=True),
        ErrosValidacaoSerializer,
    ],
    resource_type_field_name=None,
    many=False,
)


def resposta(
    modelo: Any, descricao: str, exemplos: dict[str, Any] | None = None
) -> OpenApiResponse:
    """Monta uma resposta documentada com exemplos nomeados.

    Args:
        modelo: Serializer que descreve o corpo, ou ``None`` se não há corpo.
        descricao: Texto exibido para o código de resposta.
        exemplos: Valores de exemplo, indexados pelo nome do exemplo.

    Returns:
        Resposta pronta para o ``responses`` de ``extend_schema``.
    """
    return OpenApiResponse(
        response=modelo,
        description=descricao,
        examples=[
            OpenApiExample(nome, value=valor)
            for nome, valor in (exemplos or {}).items()
        ],
    )


def exemplos_requisicao(exemplos: dict[str, Any]) -> list[OpenApiExample]:
    """Monta exemplos nomeados para o corpo da requisição.

    Em corpos que são listas, cada valor é um item: o gerador o publica
    dentro de uma lista.

    Args:
        exemplos: Valores de exemplo, indexados pelo nome do exemplo.

    Returns:
        Exemplos prontos para o ``examples`` de ``extend_schema``.
    """
    return [
        OpenApiExample(nome, value=valor, request_only=True)
        for nome, valor in exemplos.items()
    ]


def exemplo_pagina(registros: list[Any]) -> dict[str, Any]:
    """Monta o exemplo de uma página única de listagem.

    Args:
        registros: Registros que formam a página.

    Returns:
        Envelope de página com os registros em ``results``.
    """
    return {
        "links": {"next": None, "previous": None},
        "count": len(registros),
        "page": 1,
        "page_size": TAMANHO_PAGINA_PADRAO,
        "results": registros,
    }


def resposta_nao_encontrado(
    modelo: type[Model], descricao: str = "Registro não encontrado."
) -> OpenApiResponse:
    """Monta o 404 de uma rota de detalhe.

    Args:
        modelo: Model consultado pela rota; o nome dele aparece na mensagem.
        descricao: Texto exibido para o código de resposta.

    Returns:
        Resposta 404 com os textos devolvidos para UUID inexistente e para
        UUID malformado.
    """
    nome = modelo._meta.object_name
    return resposta(
        ErroDetalheSerializer,
        descricao,
        {
            "UUID inexistente": {
                "detail": f"No {nome} matches the given query."
            },
            "UUID malformado": {"detail": "Não encontrado."},
        },
    )


def parametro_uuid(descricao: str) -> OpenApiParameter:
    """Monta o parâmetro de rota ``uuid``.

    Args:
        descricao: Texto que identifica o registro.

    Returns:
        Parâmetro de rota tipado como UUID.
    """
    return OpenApiParameter(
        name="uuid",
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
        description=descricao,
    )


def parametro_ordenacao(campos: list[str], padrao: str) -> OpenApiParameter:
    """Monta o parâmetro de query ``ordering``.

    Args:
        campos: Campos aceitos para ordenar.
        padrao: Ordenação aplicada quando o parâmetro não é enviado.

    Returns:
        Parâmetro de query com os campos aceitos na descrição.
    """
    aceitos = ", ".join(f"`{campo}`" for campo in campos)
    return OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            f"Campo de ordenação: {aceitos}. Prefixe com `-` para ordem "
            "decrescente e separe vários campos por vírgula. Padrão: "
            f"`{padrao}`. Outros campos são ignorados."
        ),
    )


def parametro_busca(descricao: str) -> OpenApiParameter:
    """Monta o parâmetro de query ``search``.

    Args:
        descricao: Texto que diz onde a busca é feita.

    Returns:
        Parâmetro de query de busca textual.
    """
    return OpenApiParameter(
        name="search", type=OpenApiTypes.STR, description=descricao
    )


PARAMETRO_PAGINA = OpenApiParameter(
    name="page",
    type=OpenApiTypes.INT,
    description="Número da página, a partir de 1.",
)

PARAMETRO_TAMANHO_PAGINA = OpenApiParameter(
    name="page_size",
    type=OpenApiTypes.INT,
    description=(
        "Quantidade de registros por página. Padrão: "
        f"{TAMANHO_PAGINA_PADRAO}."
    ),
)

RESPOSTA_ACESSO_NEGADO = resposta(
    ErroAcessoSerializer,
    (
        "Credencial recusada: token JWT inválido ou expirado, token de "
        "usuário que não existe neste serviço, usuário e senha Basic "
        "incorretos ou falha de CSRF em sessão. O serviço responde 403 "
        "nesses casos, e não 401."
    ),
    {
        "Token JWT inválido": EXEMPLO_TOKEN_INVALIDO,
        "Usuário do token não encontrado": EXEMPLO_USUARIO_NAO_ENCONTRADO,
        "Usuário ou senha Basic incorretos": EXEMPLO_BASIC_INVALIDO,
    },
)

RESPOSTA_PAGINA_INEXISTENTE = resposta(
    ErroDetalheSerializer,
    "Página além da última ou valor de `page` inválido.",
    {"Página inexistente": {"detail": "Página inválida."}},
)

RESPOSTA_ERRO_INTERNO = resposta(
    None,
    "Erro inesperado no servidor. O corpo não segue um modelo JSON.",
)

RESPOSTAS_COMUNS = {
    403: RESPOSTA_ACESSO_NEGADO,
    500: RESPOSTA_ERRO_INTERNO,
}


def erro_interno(quando: str) -> OpenApiResponse:
    """Monta o 500 de uma operação com causa conhecida.

    Args:
        quando: Situação conhecida que leva ao erro, em uma frase.

    Returns:
        Resposta 500 sem modelo, com a causa na descrição.
    """
    return resposta(
        None,
        (
            f"Erro inesperado no servidor. Acontece também {quando}. O "
            "corpo não segue um modelo JSON."
        ),
    )


def respostas(especificas: dict[int, Any]) -> dict[int, Any]:
    """Junta as respostas da operação às comuns a todo o microsserviço.

    Args:
        especificas: Respostas próprias da operação, por código HTTP.

    Returns:
        Respostas ordenadas por código, incluindo 403 e 500.
    """
    return dict(sorted({**RESPOSTAS_COMUNS, **especificas}.items()))
