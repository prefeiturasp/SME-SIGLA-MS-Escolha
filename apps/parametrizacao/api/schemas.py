"""Documentação OpenAPI das operações de parametrização."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema

from core.openapi import (
    AVISO_ROTA_HERDADA,
    ERRO_LISTA_ESPERADA,
    ERROS_VALIDACAO_EM_LOTE,
    exemplos_requisicao,
    parametro_ordenacao,
    parametro_uuid,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from parametrizacao.models import Parametrizacao
from parametrizacao.serializers import (
    ParametrizacaoBulkItemSerializer,
    ParametrizacaoSerializer,
    ParametrizacoesAtualizadasSerializer,
    ParametrizacoesCriadasSerializer,
)

TAG_PARAMETRIZACAO = "Parametrização"

UUID_PARAMETRIZACAO_EXEMPLO = "5e1b7c9d-2a4f-4b6e-8d3c-9f0a1b2c3d4e"
UUID_PARAMETRIZACAO_2_EXEMPLO = "b7a6c5d4-e3f2-4a1b-9c8d-7e6f5a4b3c2d"

EXEMPLO_PARAMETRIZACAO = {
    "uuid": UUID_PARAMETRIZACAO_EXEMPLO,
    "tipo_ue": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL",
    "usar": True,
    "criado_em": "2026-03-02T10:00:00-03:00",
    "atualizado_em": "2026-03-05T14:30:00-03:00",
}

EXEMPLO_PARAMETRIZACAO_DESABILITADA = {
    "uuid": UUID_PARAMETRIZACAO_2_EXEMPLO,
    "tipo_ue": "ESCOLA MUNICIPAL DE EDUCACAO INFANTIL",
    "usar": False,
    "criado_em": "2026-03-02T10:00:00-03:00",
    "atualizado_em": "2026-03-02T10:00:00-03:00",
}

ERRO_USAR_INVALIDO = {"usar": ["Must be a valid boolean."]}

PARAMETRO_UUID = parametro_uuid("UUID da parametrização.")

RESPOSTA_PARAMETRIZACAO = resposta(
    ParametrizacaoSerializer,
    "Parametrização.",
    {"Tipo habilitado": EXEMPLO_PARAMETRIZACAO},
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(Parametrizacao)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos.",
    {"Valor que não é booleano": ERRO_USAR_INVALIDO},
)

OPERACOES_PARAMETRIZACAO = {
    "list": extend_schema(
        operation_id="listar_parametrizacoes",
        summary="Listar parametrizações",
        description=(
            "Retorna todos os tipos de unidade escolar cadastrados, em "
            "ordem alfabética, com a indicação de uso de cada um. A lista "
            "não é paginada."
        ),
        filters=False,
        parameters=[
            parametro_ordenacao(
                ["tipo_ue", "usar", "criado_em", "atualizado_em", "uuid"],
                "tipo_ue",
            )
        ],
        responses=respostas(
            {
                200: resposta(
                    ParametrizacaoSerializer(many=True),
                    "Parametrizações cadastradas.",
                    {
                        "Tipo habilitado": EXEMPLO_PARAMETRIZACAO,
                        "Tipo desabilitado": (
                            EXEMPLO_PARAMETRIZACAO_DESABILITADA
                        ),
                    },
                )
            }
        ),
    ),
    "create": extend_schema(exclude=True),
    "retrieve": extend_schema(
        operation_id="detalhar_parametrizacao",
        summary="Detalhar parametrização",
        description=(
            f"Retorna uma parametrização pelo UUID.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_PARAMETRIZACAO, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_parametrizacao",
        summary="Atualizar parametrização",
        description=(
            "Altera a indicação de uso do tipo de unidade. Só `usar` é "
            "gravado: `tipo_ue` é ignorado, e um corpo sem `usar` mantém "
            f"o valor atual.\n\n{AVISO_ROTA_HERDADA} O frontend usa a "
            "atualização em lote."
        ),
        parameters=[PARAMETRO_UUID],
        request=ParametrizacaoSerializer,
        examples=exemplos_requisicao({"Habilitar o tipo": {"usar": True}}),
        responses=respostas(
            {
                200: RESPOSTA_PARAMETRIZACAO,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_parametrizacao",
        summary="Atualizar parametrização parcialmente",
        description=(
            "Altera a indicação de uso do tipo de unidade. Tem o mesmo "
            f"efeito da atualização completa.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=ParametrizacaoSerializer,
        examples=exemplos_requisicao({"Habilitar o tipo": {"usar": True}}),
        responses=respostas(
            {
                200: RESPOSTA_PARAMETRIZACAO,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "sync": extend_schema(
        operation_id="sincronizar_parametrizacoes",
        summary="Sincronizar parametrizações com as escolas",
        description=(
            "Cria uma parametrização para cada tipo de unidade que existe "
            "no cadastro de escolas e ainda não tem uma. As novas nascem "
            "com `usar` falso, e as que já existem não mudam. A operação "
            "não recebe corpo e pode ser repetida."
        ),
        request=None,
        responses=respostas(
            {
                200: resposta(
                    ParametrizacoesCriadasSerializer,
                    "Quantidade de parametrizações criadas.",
                    {
                        "Dois tipos novos": {"created": 2},
                        "Nada a criar": {"created": 0},
                    },
                )
            }
        ),
    ),
    "bulk_update": extend_schema(
        operation_id="atualizar_parametrizacoes_em_lote",
        summary="Atualizar parametrizações em lote",
        description=(
            "Grava o valor de `usar` de várias parametrizações de uma "
            "vez. O corpo é uma lista, e todos os itens precisam ser "
            "válidos para que algum seja gravado. UUIDs que não existem "
            "são ignorados, sem erro: `updated` conta só os encontrados."
        ),
        request=ParametrizacaoBulkItemSerializer(many=True),
        examples=exemplos_requisicao(
            {
                "Habilitar um tipo": {
                    "uuid": UUID_PARAMETRIZACAO_EXEMPLO,
                    "usar": True,
                },
                "Desabilitar um tipo": {
                    "uuid": UUID_PARAMETRIZACAO_2_EXEMPLO,
                    "usar": False,
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ParametrizacoesAtualizadasSerializer,
                    "Quantidade de parametrizações gravadas.",
                    {"Duas gravadas": {"updated": 2}},
                ),
                400: resposta(
                    ERROS_VALIDACAO_EM_LOTE,
                    (
                        "Corpo inválido. Com itens inválidos, vem uma "
                        "lista com um objeto por item enviado, vazio nos "
                        "itens corretos. Se o corpo não é uma lista, vem "
                        "um único objeto."
                    ),
                    {
                        "Segundo item inválido": [
                            {},
                            {
                                "uuid": ["Must be a valid UUID."],
                                "usar": ["Este campo é obrigatório."],
                            },
                        ],
                        "Corpo que não é lista": ERRO_LISTA_ESPERADA,
                    },
                ),
            }
        ),
    ),
}
