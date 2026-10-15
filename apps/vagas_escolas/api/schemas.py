"""Documentação OpenAPI das operações de vagas das escolas."""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    Direction,
    OpenApiParameter,
    PolymorphicProxySerializer,
    extend_schema,
)

from core.openapi import (
    AVISO_ROTA_HERDADA,
    CODIGO_CARGO_EXEMPLO,
    ERRO_LISTA_ESPERADA,
    ERROS_VALIDACAO_EM_LOTE,
    NOME_CARGO_EXEMPLO,
    NOME_PROCESSO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_interno,
    exemplos_requisicao,
    parametro_uuid,
    resposta,
    resposta_nao_encontrado,
    respostas,
)
from core.serializers import ErroDetalheSerializer, ErrosValidacaoSerializer
from escola.api.schemas.dre import (
    CODIGO_DRE_EXEMPLO,
    EXEMPLO_DRE,
    NOME_DRE_EXEMPLO,
    UUID_DRE_EXEMPLO,
)
from escola.api.schemas.escola import (
    CODIGO_EOL_EXEMPLO,
    NOME_ESCOLA_EXEMPLO,
    TIPO_UE_EXEMPLO,
)
from vagas_escolas.models import VagasEscolas
from vagas_escolas.serializers import (
    DESCRICOES_VAGA,
    ErrosVagasLoteSerializer,
    ErroVagasLoteSerializer,
    LotesExcluidosSerializer,
    VagaEscolaUtilizadaItemSerializer,
    VagasEscolasListagemSerializer,
    VagasEscolasSerializer,
    VagasLoteRequisicaoSerializer,
    VagasLoteRespostaSerializer,
    VagasUtilizadasRespostaSerializer,
)

TAG_VAGAS_ESCOLAS = "Vagas das escolas"

UUID_VAGA_EXEMPLO = "9a8b7c6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
UUID_VAGA_2_EXEMPLO = "1f2e3d4c-5b6a-4978-8a9b-0c1d2e3f4a5b"
UUID_VAGA_INEXISTENTE_EXEMPLO = "c79d7b63-5a6f-4c31-988d-4374e58db023"
UUID_LOTE_EXEMPLO = "0949dff1-60f9-47bb-9779-420c16a897f1"
CODIGO_EOL_INEXISTENTE_EXEMPLO = "999999"
DATA_FECHAMENTO_EXEMPLO = "2026-03-02"

AVISO_PROCESSO_MALFORMADO = (
    "Um valor que não seja UUID não é validado e resulta em erro 500."
)

EXEMPLO_VAGA = {
    "uuid": UUID_VAGA_EXEMPLO,
    "lote_uuid": UUID_LOTE_EXEMPLO,
    "data_fechamento_modulo": DATA_FECHAMENTO_EXEMPLO,
    "cargo_codigo": CODIGO_CARGO_EXEMPLO,
    "cargo_descricao": NOME_CARGO_EXEMPLO,
    "vagas_precarias": 2,
    "vagas_precarias_utilizadas": None,
    "vagas_precarias_restantes": 2,
    "vagas_definitivas": 3,
    "vagas_definitivas_utilizadas": None,
    "vagas_definitivas_restantes": 3,
    "foi_utilizada": False,
    "esta_checada": True,
    "status": "1",
    "escola": {
        "codigo_eol": CODIGO_EOL_EXEMPLO,
        "codigo_integracao": None,
        "nome_oficial": NOME_ESCOLA_EXEMPLO,
        "dre": EXEMPLO_DRE,
        "tipo_ue": TIPO_UE_EXEMPLO,
    },
    "criado_em": "2026-03-02T10:00:00-03:00",
    "atualizado_em": "2026-03-02T10:00:00-03:00",
}

EXEMPLO_VAGA_UTILIZADA = {
    **EXEMPLO_VAGA,
    "vagas_precarias_utilizadas": 1,
    "vagas_definitivas_utilizadas": 2,
    "foi_utilizada": True,
    "atualizado_em": "2026-03-05T14:30:00-03:00",
}

EXEMPLO_LISTAGEM = {
    "vagas": [EXEMPLO_VAGA],
    "total_vagas": 5,
    "total_vagas_precarias": 2,
    "total_vagas_definitivas": 3,
    "dres": [
        {
            "codigo": CODIGO_DRE_EXEMPLO,
            "nome": NOME_DRE_EXEMPLO,
            "uuid": UUID_DRE_EXEMPLO,
        }
    ],
}

EXEMPLO_LISTAGEM_COM_UTILIZADAS = {
    **EXEMPLO_LISTAGEM,
    "vagas": [EXEMPLO_VAGA_UTILIZADA],
    "total_vagas": 3,
    "total_vagas_precarias": 1,
    "total_vagas_definitivas": 2,
}

EXEMPLO_LISTAGEM_VAZIA = {
    "vagas": [],
    "total_vagas": 0,
    "total_vagas_precarias": 0,
    "total_vagas_definitivas": 0,
    "dres": [],
}

EXEMPLO_ITEM_DO_LOTE = {
    "data_fechamento_modulo": DATA_FECHAMENTO_EXEMPLO,
    "cargo_codigo": CODIGO_CARGO_EXEMPLO,
    "cargo_descricao": NOME_CARGO_EXEMPLO,
    "codigo_eol": CODIGO_EOL_EXEMPLO,
    "vagas_precarias": 2,
    "vagas_definitivas": 3,
    "status": "1",
}

EXEMPLO_LOTE = {
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "processo_nome": NOME_PROCESSO_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "vagas": [EXEMPLO_ITEM_DO_LOTE],
}

EXEMPLO_DADOS_VAGA = {
    "data_fechamento_modulo": DATA_FECHAMENTO_EXEMPLO,
    "cargo_codigo": CODIGO_CARGO_EXEMPLO,
    "cargo_descricao": NOME_CARGO_EXEMPLO,
    "vagas_precarias": 2,
    "vagas_definitivas": 3,
    "status": "1",
}

ERRO_ESCOLA_NAO_ENCONTRADA = {
    "vaga_index": 2,
    "codigo_eol": CODIGO_EOL_INEXISTENTE_EXEMPLO,
    "error": (
        f"Escola com código EOL '{CODIGO_EOL_INEXISTENTE_EXEMPLO}' não "
        "encontrada na vaga 2"
    ),
}

EXEMPLO_LOTE_CRIADO = {
    "mensagem": "2 vagas criadas com sucesso",
    "vagas_criadas": 2,
    "total_processadas": 2,
    "lote_uuid": UUID_LOTE_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
}

EXEMPLO_LOTE_PARCIAL = {
    **EXEMPLO_LOTE_CRIADO,
    "mensagem": "1 vagas criadas com sucesso",
    "vagas_criadas": 1,
    "erros": [ERRO_ESCOLA_NAO_ENCONTRADA],
    "vagas_com_erro": 1,
}

EXEMPLO_LOTE_SEM_VAGAS = {
    "mensagem": "0 vagas criadas com sucesso",
    "vagas_criadas": 0,
    "total_processadas": 1,
    "lote_uuid": UUID_LOTE_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "erros": [
        {
            "vaga_index": 1,
            "error": (
                'Erro ao criar vaga 1: [\'O valor "02/03/2026" tem um '
                "formato de data inválido. Deve ser no formato  "
                "YYYY-MM-DD.']"
            ),
        }
    ],
    "vagas_com_erro": 1,
}

EXEMPLO_INCLUSAO = {
    **EXEMPLO_LOTE_CRIADO,
    "mensagem": "1 vagas adicionadas ao lote",
    "vagas_criadas": 1,
    "total_processadas": 1,
}

EXEMPLO_INCLUSAO_PARCIAL = {
    **EXEMPLO_LOTE_CRIADO,
    "mensagem": "1 vagas adicionadas ao lote",
    "vagas_criadas": 1,
    "erros": [ERRO_ESCOLA_NAO_ENCONTRADA],
    "vagas_com_erro": 1,
}

ERRO_CORPO_DO_LOTE = {
    "errors": {
        "processo_uuid": ["Deve ser um UUID válido."],
        "vagas": ["A lista de vagas não pode estar vazia."],
        "concurso_uuid": ["Este campo é obrigatório."],
    }
}

ERRO_VAGA_INCOMPLETA = {
    "errors": {
        "vagas": ["Campo 'data_fechamento_modulo' é obrigatório na vaga 1."]
    }
}

ERRO_TIPO_UE_DESABILITADO = {
    "detail": (
        "Tipo de unidade 'ESCOLA MUNICIPAL DE EDUCACAO INFANTIL' da "
        "escola EOL 019455 está desabilitado."
    ),
    "code": "TIPO_UE_DESABILITADO",
}


class VagasEscolasExtension(OpenApiSerializerExtension):
    """Publica ``status`` como texto, sem prender às opções do campo."""

    target_class = VagasEscolasSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema da vaga com ``status`` em texto livre."""
        esquema: dict[str, Any] = auto_schema._map_serializer(
            self.target, direction, bypass_extensions=True
        )
        esquema["properties"]["status"] = {
            "type": "string",
            "maxLength": 20,
            "description": DESCRICOES_VAGA["status"]["help_text"],
        }
        return esquema


ERRO_LOTE_DE_VAGAS = PolymorphicProxySerializer(
    component_name="ErroLoteDeVagas",
    serializers=[
        VagasLoteRespostaSerializer,
        ErrosVagasLoteSerializer,
        ErroVagasLoteSerializer,
    ],
    resource_type_field_name=None,
    many=False,
)

PARAMETRO_UUID = parametro_uuid("UUID da vaga.")

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="processo_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Retorna apenas as vagas do lote mais recente do processo de "
            "convocação. Sem o parâmetro, entram as vagas de todos os "
            f"lotes. {AVISO_PROCESSO_MALFORMADO}"
        ),
    ),
    OpenApiParameter(
        name="cargo_codigo",
        type=OpenApiTypes.INT,
        description="Retorna apenas as vagas do cargo com o código informado.",
    ),
    OpenApiParameter(
        name="escola__codigo_eol",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas as vagas da escola com o código EOL informado."
        ),
    ),
    OpenApiParameter(
        name="escola__dre__codigo",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas as vagas das escolas da DRE com o código "
            "informado."
        ),
    ),
]

PARAMETROS_POR_CARGO_E_ESCOLAS = [
    OpenApiParameter(
        name="cargo_codigo",
        type=OpenApiTypes.INT,
        description=(
            "Retorna apenas as vagas do cargo com o código informado. Um "
            "valor não numérico resulta em erro 500."
        ),
    ),
    OpenApiParameter(
        name="codigo_eol",
        type=OpenApiTypes.STR,
        many=True,
        description=(
            "Retorna apenas as vagas da escola com o código EOL "
            "informado. Repita o parâmetro para várias escolas."
        ),
    ),
    OpenApiParameter(
        name="codigo_eol__in",
        type=OpenApiTypes.STR,
        description=(
            "Códigos EOL separados por vírgula. Só é considerado quando "
            "`codigo_eol` não é enviado."
        ),
    ),
]

RESPOSTA_VAGA = resposta(
    VagasEscolasSerializer, "Vaga.", {"Vaga": EXEMPLO_VAGA}
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(VagasEscolas)

RESPOSTA_CORPO_DO_LOTE_INVALIDO = resposta(
    ErrosVagasLoteSerializer,
    "Corpo inválido. Nada é gravado.",
    {
        "Campos inválidos": ERRO_CORPO_DO_LOTE,
        "Vaga sem campo obrigatório": ERRO_VAGA_INCOMPLETA,
    },
)

RESPOSTA_ERRO_EM_LOTE = resposta(
    ERROS_VALIDACAO_EM_LOTE,
    (
        "Corpo inválido. Com itens inválidos, vem uma lista com um objeto "
        "por item enviado, vazio nos itens corretos. Se o corpo não é uma "
        "lista, vem um único objeto."
    ),
    {
        "Item inválido": [
            {
                "uuid": ["Must be a valid UUID."],
                "foi_utilizada": ["Este campo é obrigatório."],
            }
        ],
        "Quantidade nula": [
            {"vagas_precarias_utilizadas": ["Este campo não pode ser nulo."]}
        ],
        "Corpo que não é lista": ERRO_LISTA_ESPERADA,
    },
)

OPERACOES_VAGAS_ESCOLAS = {
    "list": extend_schema(
        operation_id="listar_vagas_escolas",
        summary="Listar vagas das escolas",
        description=(
            "Retorna as vagas selecionadas (`esta_checada` verdadeiro), "
            "com os totais e as DREs das escolas listadas. A lista não é "
            "paginada.\n\n"
            "Com `processo_uuid`, valem só as vagas do lote mais recente "
            "do processo. Os totais somam as quantidades utilizadas se "
            "alguma vaga da listagem já as tem, e as ofertadas caso "
            "contrário."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    VagasEscolasListagemSerializer,
                    "Vagas, totais e DREs.",
                    {
                        "Vagas ofertadas": EXEMPLO_LISTAGEM,
                        "Com vagas utilizadas": (
                            EXEMPLO_LISTAGEM_COM_UTILIZADAS
                        ),
                        "Processo sem lote": EXEMPLO_LISTAGEM_VAZIA,
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtro `cargo_codigo` com valor não numérico.",
                    {
                        "Código não numérico": {
                            "cargo_codigo": ["Informe um número."]
                        }
                    },
                ),
                500: erro_interno("quando `processo_uuid` não é um UUID"),
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_vagas_escolas_em_lote",
        summary="Criar lote de vagas de um processo",
        description=(
            "Cria um lote novo para o processo e grava nele as vagas "
            "enviadas. Cada vaga é processada em separado: a escola é "
            "localizada pelo código EOL, e as vagas restantes começam "
            "iguais às ofertadas.\n\n"
            "- **201**: todas as vagas foram gravadas.\n"
            "- **207**: parte das vagas falhou. As demais ficam gravadas, "
            "e `erros` lista as que falharam.\n"
            "- **400**: nenhuma vaga foi gravada, o corpo é inválido ou o "
            "lote traz escola de um tipo de unidade desabilitado. Quando "
            "todas as vagas falham, o lote fica criado mesmo assim, "
            "vazio.\n\n"
            "Cada envio cria um lote, e as consultas por processo usam o "
            "mais recente: um novo envio substitui o anterior nas "
            "listagens."
        ),
        request=VagasLoteRequisicaoSerializer,
        examples=exemplos_requisicao({"Lote com uma vaga": EXEMPLO_LOTE}),
        responses=respostas(
            {
                201: resposta(
                    VagasLoteRespostaSerializer,
                    "Lote criado com todas as vagas.",
                    {"Lote criado": EXEMPLO_LOTE_CRIADO},
                ),
                207: resposta(
                    VagasLoteRespostaSerializer,
                    "Lote criado com parte das vagas.",
                    {"Escola não encontrada": EXEMPLO_LOTE_PARCIAL},
                ),
                400: resposta(
                    ERRO_LOTE_DE_VAGAS,
                    (
                        "Lote recusado. O corpo traz o resultado do "
                        "processamento quando nenhuma vaga foi gravada, "
                        "`errors` quando o corpo é inválido, ou `detail` e "
                        "`code` quando há escola de tipo de unidade "
                        "desabilitado."
                    ),
                    {
                        "Nenhuma vaga gravada": EXEMPLO_LOTE_SEM_VAGAS,
                        "Campos inválidos": ERRO_CORPO_DO_LOTE,
                        "Vaga sem campo obrigatório": ERRO_VAGA_INCOMPLETA,
                        "Tipo de unidade desabilitado": (
                            ERRO_TIPO_UE_DESABILITADO
                        ),
                    },
                ),
                500: resposta(
                    ErroVagasLoteSerializer,
                    (
                        "Falha inesperada ao gravar o lote; nada é "
                        "gravado. Um corpo que não é um objeto JSON "
                        "também responde 500, mas sem corpo JSON."
                    ),
                    {
                        "Falha ao gravar": {
                            "detail": "connection already closed",
                            "code": "ERRO_AO_CRIAR_VAGAS_EM_LOTE",
                        }
                    },
                ),
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_vaga_escola",
        summary="Detalhar vaga",
        description=f"Retorna uma vaga pelo UUID.\n\n{AVISO_ROTA_HERDADA}",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_VAGA, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_vaga_escola",
        summary="Atualizar vaga",
        description=(
            "Substitui os dados da vaga. A escola e o lote não mudam. "
            "`data_fechamento_modulo`, `cargo_codigo` e `cargo_descricao` "
            "são obrigatórios; os demais campos mantêm o valor atual "
            "quando omitidos. As quantidades restantes não são "
            "recalculadas: valem as enviadas.\n\n"
            f"{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=VagasEscolasSerializer,
        examples=exemplos_requisicao({"Dados da vaga": EXEMPLO_DADOS_VAGA}),
        responses=respostas(
            {
                200: RESPOSTA_VAGA,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {
                        "Campos ausentes": {
                            "data_fechamento_modulo": [
                                "Este campo é obrigatório."
                            ],
                            "cargo_codigo": ["Este campo é obrigatório."],
                            "cargo_descricao": ["Este campo é obrigatório."],
                        }
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_vaga_escola",
        summary="Atualizar vaga parcialmente",
        description=(
            "Altera apenas os campos enviados. As quantidades restantes "
            f"não são recalculadas.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=VagasEscolasSerializer,
        examples=exemplos_requisicao(
            {"Aumentar as vagas definitivas": {"vagas_definitivas": 5}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_VAGA,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {
                        "Situação fora das opções": {
                            "status": ['"9" não é um escolha válido.']
                        }
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_vaga_escola",
        summary="Excluir vaga",
        description=(
            "Exclui a vaga definitivamente. As escolhas feitas nela "
            f"continuam, mas ficam sem vaga.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Vaga excluída."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "utilizadas": extend_schema(
        operation_id="atualizar_vagas_utilizadas",
        summary="Atualizar vagas utilizadas",
        description=(
            "Informa, para várias vagas de uma vez, se cada uma será "
            "usada no processo e quantas vagas precárias e definitivas "
            "serão usadas. `esta_checada` recebe o mesmo valor de "
            "`foi_utilizada`: uma vaga marcada com `false` sai da "
            "listagem.\n\n"
            "O corpo é uma lista, e todos os itens precisam ser válidos "
            "para que algum seja gravado. UUIDs que não existem não geram "
            "erro: voltam em `nao_encontrados`."
        ),
        request=VagaEscolaUtilizadaItemSerializer(many=True),
        examples=exemplos_requisicao(
            {
                "Usar uma vaga": {
                    "uuid": UUID_VAGA_EXEMPLO,
                    "foi_utilizada": True,
                    "vagas_precarias_utilizadas": 1,
                    "vagas_definitivas_utilizadas": 2,
                },
                "Dispensar uma vaga": {
                    "uuid": UUID_VAGA_2_EXEMPLO,
                    "foi_utilizada": False,
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    VagasUtilizadasRespostaSerializer,
                    "Vagas gravadas e UUIDs não encontrados.",
                    {
                        "Duas gravadas e uma não encontrada": {
                            "atualizados": [
                                UUID_VAGA_EXEMPLO,
                                UUID_VAGA_2_EXEMPLO,
                            ],
                            "nao_encontrados": [UUID_VAGA_INEXISTENTE_EXEMPLO],
                            "total": 2,
                        }
                    },
                ),
                400: RESPOSTA_ERRO_EM_LOTE,
            }
        ),
    ),
    "atualizar_vagas_lote": extend_schema(
        operation_id="incluir_vagas_no_lote",
        summary="Incluir vagas no lote de um processo",
        description=(
            "Grava as vagas enviadas no lote mais recente do processo, "
            "sem criar lote novo. O corpo é o mesmo da criação do lote: "
            "`concurso_uuid` é exigido, embora não seja usado aqui. Cada "
            "vaga é processada em separado.\n\n"
            "- **201**: todas as vagas foram gravadas.\n"
            "- **207**: ao menos uma vaga falhou, inclusive quando "
            "nenhuma é gravada. `erros` lista as que falharam.\n"
            "- **404**: o processo não tem lote.\n\n"
            "Diferente da criação do lote, esta rota não recusa escolas "
            "de tipo de unidade desabilitado."
        ),
        request=VagasLoteRequisicaoSerializer,
        examples=exemplos_requisicao({"Incluir uma vaga": EXEMPLO_LOTE}),
        responses=respostas(
            {
                201: resposta(
                    VagasLoteRespostaSerializer,
                    "Todas as vagas foram incluídas no lote.",
                    {"Vaga incluída": EXEMPLO_INCLUSAO},
                ),
                207: resposta(
                    VagasLoteRespostaSerializer,
                    "Ao menos uma vaga não foi incluída.",
                    {"Escola não encontrada": EXEMPLO_INCLUSAO_PARCIAL},
                ),
                400: RESPOSTA_CORPO_DO_LOTE_INVALIDO,
                404: resposta(
                    ErroDetalheSerializer,
                    "O processo não tem lote de vagas.",
                    {
                        "Processo sem lote": {
                            "detail": (
                                "Lote não encontrado para o processo "
                                "informado"
                            )
                        }
                    },
                ),
            }
        ),
    ),
    "por_cargo_e_escolas": extend_schema(
        operation_id="listar_vagas_por_cargo_e_escolas",
        summary="Listar vagas por cargo e escolas",
        description=(
            "Retorna as vagas de um cargo, de um conjunto de escolas ou "
            "dos dois, em todos os lotes e sem considerar `esta_checada`. "
            "Sem parâmetros, retorna todas as vagas. A lista não é "
            "paginada."
        ),
        parameters=PARAMETROS_POR_CARGO_E_ESCOLAS,
        responses=respostas(
            {
                200: resposta(
                    VagasEscolasSerializer(many=True),
                    "Vagas encontradas.",
                    {"Vaga": EXEMPLO_VAGA},
                ),
                500: erro_interno("quando `cargo_codigo` não é numérico"),
            }
        ),
    ),
    "excluir_por_processo": extend_schema(
        operation_id="excluir_vagas_por_processo",
        summary="Excluir as vagas de um processo",
        description=(
            "Exclui definitivamente todos os lotes do processo e as vagas "
            "de cada um. As escolhas feitas nessas vagas continuam, mas "
            "ficam sem vaga. Responde 200 também quando o processo não "
            "tem lote."
        ),
        parameters=[
            OpenApiParameter(
                name="processo_uuid",
                type=OpenApiTypes.UUID,
                required=True,
                description=(
                    "UUID do processo de convocação. "
                    f"{AVISO_PROCESSO_MALFORMADO}"
                ),
            )
        ],
        responses=respostas(
            {
                200: resposta(
                    LotesExcluidosSerializer,
                    "Quantidade de registros apagados.",
                    {
                        "Um lote com duas vagas": {"lotes_excluidos": 3},
                        "Processo sem lote": {"lotes_excluidos": 0},
                    },
                ),
                400: resposta(
                    ErroDetalheSerializer,
                    "Parâmetro `processo_uuid` ausente.",
                    {
                        "Processo não informado": {
                            "detail": "processo_uuid é obrigatório."
                        }
                    },
                ),
                500: erro_interno("quando `processo_uuid` não é um UUID"),
            }
        ),
    ),
}
