"""Documentação OpenAPI da extração de dados de escolhas."""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction, extend_schema

from core.openapi import (
    CODIGO_CARGO_EXEMPLO,
    NOME_CARGO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    exemplos_requisicao,
    resposta,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from escola.api.schemas.dre import NOME_DRE_EXEMPLO
from escolhas.serializers import (
    ExtracaoDadosAnoSerializer,
    ExtracaoDadosRespostaSerializer,
    ExtracaoDadosSerializer,
)

TAG_EXTRACAO_DADOS = "Extração de dados"

ULTIMA_ESCOLHA_EXEMPLO = "2026-03-10T12:15:00+00:00"

EXEMPLO_CONTAGENS = {
    "escolha": {"total": 17, "geral": 12, "pcd": 2, "nna": 3},
    "nao-escolha": {"total": 4, "geral": 3, "pcd": 0, "nna": 1},
    "reconvocacao": {"total": 2, "geral": 2, "pcd": 0, "nna": 0},
}

EXEMPLO_CONTAGENS_ZERADAS = {
    "escolha": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
    "nao-escolha": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
    "reconvocacao": {"total": 0, "geral": 0, "pcd": 0, "nna": 0},
}

EXEMPLO_DRE = {"nome": NOME_DRE_EXEMPLO, "escolhas": 17, "vagas": 40}

EXEMPLO_DRES_CONCURSOS = {
    UUID_CONCURSO_EXEMPLO: [
        {
            **EXEMPLO_DRE,
            "codigo_cargo": CODIGO_CARGO_EXEMPLO,
            "cargo_descricao": NOME_CARGO_EXEMPLO,
            "ultima_escolha_em": ULTIMA_ESCOLHA_EXEMPLO,
        }
    ]
}

EXEMPLO_SEM_FILTROS = {
    **EXEMPLO_CONTAGENS,
    "dres": [EXEMPLO_DRE],
    "dres_concursos": EXEMPLO_DRES_CONCURSOS,
    "ultima_escolha_em": ULTIMA_ESCOLHA_EXEMPLO,
}

EXEMPLO_COM_FILTROS = {
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "filtros": [
        {"ano": 2025, "processo_uuids": []},
        {"ano": 2026, "processo_uuids": [UUID_PROCESSO_EXEMPLO]},
    ],
    "2025": {
        **EXEMPLO_CONTAGENS_ZERADAS,
        "dres": [{"nome": NOME_DRE_EXEMPLO, "escolhas": 0, "vagas": 40}],
    },
    "2026": {**EXEMPLO_CONTAGENS, "dres": [EXEMPLO_DRE]},
    "dres_concursos": EXEMPLO_DRES_CONCURSOS,
    "ultima_escolha_em": ULTIMA_ESCOLHA_EXEMPLO,
}


class ExtracaoDadosRespostaExtension(OpenApiSerializerExtension):
    """Acrescenta as chaves de ano aos totais da extração de dados."""

    target_class = ExtracaoDadosRespostaSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema dos totais, com uma chave por ano."""
        esquema: dict[str, Any] = auto_schema._map_serializer(
            self.target, direction, bypass_extensions=True
        )
        esquema["additionalProperties"] = auto_schema.resolve_serializer(
            ExtracaoDadosAnoSerializer, direction
        ).ref
        return esquema


OPERACOES_EXTRACAO_DADOS = {
    "create": extend_schema(
        operation_id="extrair_dados_escolhas",
        summary="Extrair dados de escolhas",
        description=(
            "Retorna os totais de escolhas por situação e por categoria "
            "do candidato, as escolhas e as vagas por DRE e o detalhe "
            "por concurso, DRE e cargo. A consulta usa POST para receber "
            "o recorte no corpo e não altera nada.\n\n"
            "Sem `filtros`, os totais vêm na raiz. Com `filtros`, vêm "
            "separados em uma chave por ano, e a raiz ganha `filtros` e, "
            "se enviado, `concurso_uuid`. `dres_concursos` e "
            "`ultima_escolha_em` vêm sempre na raiz.\n\n"
            "As categorias vêm do MS-Candidatos. Se ele não responde, a "
            "resposta continua 200, com `geral`, `pcd` e `nna` zerados e "
            "só `total` preenchido."
        ),
        request=ExtracaoDadosSerializer,
        examples=exemplos_requisicao(
            {
                "Um concurso, sem separar por ano": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO
                },
                "Um concurso em dois anos": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "filtros": [
                        {"ano": 2025},
                        {
                            "ano": 2026,
                            "processo_uuids": [UUID_PROCESSO_EXEMPLO],
                        },
                    ],
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ExtracaoDadosRespostaSerializer,
                    "Totais do recorte pedido.",
                    {
                        "Sem filtros": EXEMPLO_SEM_FILTROS,
                        "Com filtros de ano": EXEMPLO_COM_FILTROS,
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Recorte inválido.",
                    {
                        "Mais de dois anos": {
                            "filtros": {
                                "non_field_errors": [
                                    "Ensure this field has no more than 2 "
                                    "elements."
                                ]
                            }
                        },
                        "Ano e processo inválidos": {
                            "concurso_uuid": ["Must be a valid UUID."],
                            "filtros": [
                                {
                                    "ano": [
                                        "Certifque-se de que este valor "
                                        "seja maior ou igual a 1000."
                                    ],
                                    "processo_uuids": {
                                        "0": ["Must be a valid UUID."]
                                    },
                                }
                            ],
                        },
                    },
                ),
            }
        ),
    ),
}
