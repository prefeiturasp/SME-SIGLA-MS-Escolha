"""Documentação OpenAPI das consultas de escolhas."""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import Direction, OpenApiParameter, extend_schema

from core.openapi import (
    CODIGO_CARGO_EXEMPLO,
    NOME_CARGO_EXEMPLO,
    UUID_CANDIDATO_2_EXEMPLO,
    UUID_CANDIDATO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_interno,
    exemplos_requisicao,
    resposta,
    respostas,
)
from core.serializers import ErroDetalheSerializer
from escolhas.api.schemas.comuns import (
    AVISO_CONSULTA_POR_POST,
    AVISO_UUID_MALFORMADO,
    ERRO_INTERNO_UUID_MALFORMADO,
    EXEMPLO_ESCOLHA_LISTADA,
    PARAMETRO_FIELDS,
    UUID_ESCOLHA_2_EXEMPLO,
)
from escolhas.serializers import (
    BuscaEscolhasRequisicaoSerializer,
    CandidatoEncontradoSerializer,
    EscolhaListSerializer,
    EscolhaReconvocacaoSerializer,
    EscolhasDoProcessoSerializer,
    EscolhasPorConvocacaoRequisicaoSerializer,
    EscolhasPorProcessoSerializer,
    RepassadoDoMsCandidatosSerializer,
)

UUID_PROCESSO_SEM_ESCOLHAS_EXEMPLO = "a5e2c558-a499-47f2-8efa-89bd6b507dfd"
UUID_PESSOA_EXEMPLO = "5a4b3c2d-1e0f-4a9b-8c7d-6e5f4a3b2c1d"

ESQUEMA_TOTAL_POR_CARGO = {
    "type": "object",
    "description": (
        "Total de escolhas por cargo. Cada chave é o código de um cargo e "
        "o valor é a quantidade de escolhas."
    ),
    "additionalProperties": {"type": "integer"},
}

EXEMPLO_ESCOLHAS_POR_PROCESSO = {
    UUID_PROCESSO_EXEMPLO: {
        "escolha": {
            "total": 1,
            "candidatos_uuids": [UUID_CANDIDATO_EXEMPLO],
        },
        "nao-escolha": {"total": 0, "candidatos_uuids": []},
        "reconvocacao": {
            "total": 1,
            "candidatos_uuids": [UUID_CANDIDATO_2_EXEMPLO],
        },
    },
    UUID_PROCESSO_SEM_ESCOLHAS_EXEMPLO: {
        "escolha": {"total": 0, "candidatos_uuids": []},
        "nao-escolha": {"total": 0, "candidatos_uuids": []},
        "reconvocacao": {"total": 0, "candidatos_uuids": []},
    },
}

EXEMPLO_CANDIDATO_ENCONTRADO = {
    "id": 4821,
    "uuid": UUID_PESSOA_EXEMPLO,
    "nome": "Maria Aparecida da Silva",
    "cpf": "12345678909",
    "rg": "123456789",
    "registro_funcional": "1234567",
    "concursos": [
        {
            "id": 15230,
            "uuid": UUID_CANDIDATO_EXEMPLO,
            "concurso_uuid": UUID_CONCURSO_EXEMPLO,
            "concurso_nome": "Concurso Professor de Educação Infantil 2025",
            "codigo_cargo": str(CODIGO_CARGO_EXEMPLO),
            "descricao_cargo": NOME_CARGO_EXEMPLO,
            "classificacao": 12,
            "categoria_efetiva": "GERAL",
            "eliminado": False,
        }
    ],
}

PARAMETROS_BUSCA_DE_CANDIDATOS = [
    OpenApiParameter(
        name="nome",
        type=OpenApiTypes.STR,
        description="Trecho do nome do candidato.",
    ),
    OpenApiParameter(
        name="cpf",
        type=OpenApiTypes.STR,
        description="CPF do candidato, ou parte dele.",
    ),
    OpenApiParameter(
        name="rg",
        type=OpenApiTypes.STR,
        description="RG do candidato, ou parte dele.",
    ),
    OpenApiParameter(
        name="registro_funcional",
        type=OpenApiTypes.STR,
        description="Registro funcional do candidato, ou parte dele.",
    ),
]


class EscolhasPorProcessoExtension(OpenApiSerializerExtension):
    """Descreve a resposta como mapa de processo para candidatos."""

    target_class = EscolhasPorProcessoSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema do mapa de processos."""
        return {
            "type": "object",
            "description": (
                "Candidatos por processo de convocação. Cada chave é o "
                "UUID de um processo informado na requisição, e o valor "
                "traz os candidatos dele por situação da escolha."
            ),
            "additionalProperties": auto_schema.resolve_serializer(
                EscolhasDoProcessoSerializer, direction
            ).ref,
        }


class RepassadoDoMsCandidatosExtension(OpenApiSerializerExtension):
    """Aceita campos além dos descritos nos modelos do MS-Candidatos."""

    target_class = RepassadoDoMsCandidatosSerializer
    match_subclasses = True

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema dos campos descritos, aberto a outros campos."""
        esquema: dict[str, Any] = auto_schema._map_serializer(
            self.target, direction, bypass_extensions=True
        )
        esquema["additionalProperties"] = True
        return esquema


OPERACOES_CONSULTAS = {
    "busca": extend_schema(
        operation_id="buscar_escolhas_por_candidatos",
        summary="Buscar escolhas por candidatos",
        description=(
            "Retorna as escolhas dos habilitados informados, da mais "
            "recente para a mais antiga, cada uma com os dados da vaga e "
            "o histórico. A lista não é paginada. "
            f"{AVISO_CONSULTA_POR_POST}\n\n{AVISO_UUID_MALFORMADO}"
        ),
        parameters=[PARAMETRO_FIELDS],
        request=BuscaEscolhasRequisicaoSerializer,
        examples=exemplos_requisicao(
            {
                "Dois candidatos de um concurso": {
                    "candidato_uuid": [
                        UUID_CANDIDATO_EXEMPLO,
                        UUID_CANDIDATO_2_EXEMPLO,
                    ],
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    EscolhaListSerializer(many=True),
                    "Escolhas encontradas. Lista vazia se não há nenhuma.",
                    {"Escolha": EXEMPLO_ESCOLHA_LISTADA},
                ),
                400: resposta(
                    ErroDetalheSerializer,
                    "`candidato_uuid` não é uma lista.",
                    {
                        "Valor que não é lista": {
                            "detail": (
                                "candidato_uuid deve ser uma lista de UUIDs."
                            )
                        }
                    },
                ),
                500: ERRO_INTERNO_UUID_MALFORMADO,
            }
        ),
    ),
    "busca_por_convocacao": extend_schema(
        operation_id="agregar_escolhas_por_convocacao",
        summary="Agregar escolhas por processo de convocação",
        description=(
            "Para cada processo informado, retorna os candidatos "
            "separados pela situação da escolha, com o total de cada "
            "situação. Vale o processo gravado na própria escolha, e "
            "processos sem escolhas vêm com as três situações zeradas. "
            f"{AVISO_CONSULTA_POR_POST}\n\n{AVISO_UUID_MALFORMADO}"
        ),
        request=EscolhasPorConvocacaoRequisicaoSerializer,
        examples=exemplos_requisicao(
            {
                "Dois processos": {
                    "processo_uuids": [
                        UUID_PROCESSO_EXEMPLO,
                        UUID_PROCESSO_SEM_ESCOLHAS_EXEMPLO,
                    ]
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    EscolhasPorProcessoSerializer,
                    "Candidatos de cada processo, por situação.",
                    {
                        "Um processo com escolhas e outro sem": (
                            EXEMPLO_ESCOLHAS_POR_PROCESSO
                        )
                    },
                ),
                400: resposta(
                    ErroDetalheSerializer,
                    "`processo_uuids` ausente, vazio ou que não é lista.",
                    {
                        "Lista ausente": {
                            "detail": (
                                "processo_uuids é obrigatório e deve ser "
                                "uma lista"
                            )
                        }
                    },
                ),
                500: ERRO_INTERNO_UUID_MALFORMADO,
            }
        ),
    ),
    "reconvocacao": extend_schema(
        operation_id="listar_escolhas_reconvocacao",
        summary="Listar escolhas em reconvocação",
        description=(
            "Retorna o identificador e o candidato de todas as escolhas "
            "em situação de reconvocação, de qualquer concurso, da mais "
            "recente para a mais antiga. A rota não aceita filtros nem "
            "paginação, e o parâmetro `fields` das outras consultas "
            "resulta aqui em erro 500."
        ),
        responses=respostas(
            {
                200: resposta(
                    EscolhaReconvocacaoSerializer(many=True),
                    "Escolhas em reconvocação.",
                    {
                        "Escolha": {
                            "uuid": UUID_ESCOLHA_2_EXEMPLO,
                            "candidato_uuid": UUID_CANDIDATO_2_EXEMPLO,
                        }
                    },
                ),
                500: erro_interno("quando o parâmetro `fields` é enviado"),
            }
        ),
    ),
    "buscar_candidatos": extend_schema(
        operation_id="buscar_candidatos",
        summary="Buscar candidatos no MS-Candidatos",
        description=(
            "Repassa a busca ao MS-Candidatos e devolve a resposta dele, "
            "trocando `descricao_cargo` pelo nome do cargo cadastrado no "
            "MS-Concursos quando o código do cargo é encontrado lá. "
            "Informe ao menos um parâmetro; os informados são "
            "combinados, e todos precisam casar.\n\n"
            "O modelo descreve os campos principais. A lista completa "
            "está na operação `buscar_candidatos` da documentação do "
            "MS-Candidatos.\n\n"
            "Se o MS-Candidatos não responde, a resposta é 400. Se o "
            "MS-Concursos não responde, os candidatos vêm com o "
            "`descricao_cargo` original."
        ),
        parameters=PARAMETROS_BUSCA_DE_CANDIDATOS,
        responses=respostas(
            {
                200: resposta(
                    CandidatoEncontradoSerializer(many=True),
                    "Candidatos encontrados. Lista vazia se nenhum casa.",
                    {"Candidato": EXEMPLO_CANDIDATO_ENCONTRADO},
                ),
                400: resposta(
                    ErroDetalheSerializer,
                    (
                        "Nenhum parâmetro de busca informado, ou falha ao "
                        "consultar o MS-Candidatos."
                    ),
                    {
                        "Sem parâmetros": {
                            "detail": (
                                "Informe pelo menos um parâmetro: nome, "
                                "cpf, rg ou registro_funcional."
                            )
                        },
                        "MS-Candidatos indisponível": {
                            "detail": (
                                "Erro ao consultar serviço de candidatos."
                            )
                        },
                    },
                ),
            }
        ),
    ),
    "agrupar_por_cargo": extend_schema(
        operation_id="contar_escolhas_por_cargo",
        summary="Contar escolhas por cargo",
        description=(
            "Retorna, para cada cargo, quantas escolhas na situação "
            "`escolha` existem em vagas dele, em todos os concursos e "
            "processos. Escolhas nessa situação que não têm vaga são "
            "somadas na chave `None`."
        ),
        responses=respostas(
            {
                200: resposta(
                    ESQUEMA_TOTAL_POR_CARGO,
                    "Total de escolhas por código de cargo.",
                    {
                        "Dois cargos": {
                            str(CODIGO_CARGO_EXEMPLO): 17,
                            "3860": 4,
                        }
                    },
                ),
            }
        ),
    ),
}
