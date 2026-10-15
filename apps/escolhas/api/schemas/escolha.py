"""Documentação OpenAPI do cadastro de escolhas."""

from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    PolymorphicProxySerializer,
    extend_schema,
)

from core.openapi import (
    AVISO_ROTA_HERDADA,
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
    RESPOSTA_PAGINA_INEXISTENTE,
    UUID_CANDIDATO_2_EXEMPLO,
    UUID_CANDIDATO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
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
from escolhas.api.schemas.comuns import (
    EXEMPLO_ESCOLHA,
    EXEMPLO_ESCOLHA_LISTADA,
    EXEMPLO_NAO_ESCOLHA,
    PARAMETRO_FIELDS,
)
from escolhas.constants import SituacaoChoices
from escolhas.models import Escolha
from escolhas.serializers import (
    EscolhaDetalheSerializer,
    EscolhaListSerializer,
    EscolhaPaginadaSerializer,
    EscolhaSerializer,
)
from vagas_escolas.api.schemas import UUID_VAGA_EXEMPLO

AVISO_SEM_RECALCULO = (
    "Uma mudança de situação gera um registro no histórico, mas as vagas "
    "restantes não são recalculadas: só a criação desconta vaga. Enviar "
    "`vaga_escola_uuid` nulo não desfaz o vínculo com a vaga atual."
)

EXEMPLO_NOVA_ESCOLHA = {
    "candidato_uuid": UUID_CANDIDATO_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "situacao": "escolha",
    "tipo_vaga": "definitiva",
    "vaga_escola_uuid": UUID_VAGA_EXEMPLO,
}

EXEMPLO_NOVA_NAO_ESCOLHA = {
    "candidato_uuid": UUID_CANDIDATO_2_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "situacao": "nao-escolha",
}

ERRO_TIPO_DE_VAGA_AUSENTE = {
    "tipo_vaga": ['Este campo é obrigatório quando a situação é "escolha".']
}

ERRO_VAGA_AUSENTE = {
    "vaga_escola_uuid": [
        'Este campo é obrigatório quando a situação é "escolha".'
    ]
}

ERRO_VAGA_INEXISTENTE = {
    "vaga_escola_uuid": [
        f"VagaEscola com UUID {UUID_VAGA_EXEMPLO} não encontrada."
    ]
}

LISTAGEM_ESCOLHAS = PolymorphicProxySerializer(
    component_name="EscolhaListagem",
    serializers=[
        EscolhaPaginadaSerializer,
        EscolhaListSerializer(many=True),
    ],
    resource_type_field_name=None,
    many=False,
)

PARAMETRO_UUID = parametro_uuid("UUID da escolha.")

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="candidato_uuid",
        type=OpenApiTypes.UUID,
        description="Retorna apenas as escolhas do habilitado informado.",
    ),
    OpenApiParameter(
        name="concurso_uuid",
        type=OpenApiTypes.UUID,
        description="Retorna apenas as escolhas do concurso informado.",
    ),
    OpenApiParameter(
        name="processo_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Retorna apenas as escolhas registradas no processo de "
            "convocação informado."
        ),
    ),
    OpenApiParameter(
        name="situacao",
        type=OpenApiTypes.STR,
        enum=SituacaoChoices.values,
        description="Retorna apenas as escolhas na situação informada.",
    ),
    OpenApiParameter(
        name="situacao__in",
        type=OpenApiTypes.STR,
        many=True,
        explode=False,
        enum=SituacaoChoices.values,
        description=(
            "Retorna as escolhas em qualquer das situações informadas, "
            "separadas por vírgula, por exemplo `escolha,reconvocacao`. "
            "Valores desconhecidos são ignorados."
        ),
    ),
    OpenApiParameter(
        name="vaga_escola__cargo_codigo",
        type=OpenApiTypes.INT,
        description=(
            "Retorna apenas as escolhas em vagas do cargo com o código "
            "informado."
        ),
    ),
    OpenApiParameter(
        name="vaga_escola__lote__processo_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Retorna apenas as escolhas cuja vaga pertence a um lote do "
            "processo de convocação informado."
        ),
    ),
    parametro_busca("Busca por trecho da situação ou do tipo de vaga."),
    parametro_ordenacao(["criado_em"], "-criado_em"),
    OpenApiParameter(
        name="no_page",
        type=OpenApiTypes.STR,
        description=(
            "Desliga a paginação: a resposta passa a ser um array simples "
            "com todas as escolhas. Basta o parâmetro estar presente, "
            "com qualquer valor, inclusive `false`."
        ),
    ),
    PARAMETRO_FIELDS,
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
]

RESPOSTA_ESCOLHA = resposta(
    EscolhaDetalheSerializer,
    "Escolha.",
    {"Escolha de vaga definitiva": EXEMPLO_ESCOLHA},
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(Escolha)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos.",
    {
        "Campos ausentes": {
            "candidato_uuid": ["Este campo é obrigatório."],
            "concurso_uuid": ["Este campo é obrigatório."],
            "situacao": ["Este campo é obrigatório."],
        },
        "Escolha sem tipo de vaga": ERRO_TIPO_DE_VAGA_AUSENTE,
        "Escolha sem vaga": ERRO_VAGA_AUSENTE,
        "Vaga inexistente": ERRO_VAGA_INEXISTENTE,
    },
)

OPERACOES_CADASTRO = {
    "list": extend_schema(
        operation_id="listar_escolhas",
        summary="Listar escolhas",
        description=(
            "Retorna as escolhas, da mais recente para a mais antiga, "
            "cada uma com os dados da vaga e o histórico de situações. A "
            "resposta vem em páginas, ou em um array simples quando "
            "`no_page` é enviado."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    LISTAGEM_ESCOLHAS,
                    "Página de escolhas, ou array simples com `no_page`.",
                    {
                        "Página": exemplo_pagina([EXEMPLO_ESCOLHA_LISTADA]),
                        "Sem paginação": [EXEMPLO_ESCOLHA_LISTADA],
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtro com valor inválido.",
                    {
                        "UUID malformado": {
                            "candidato_uuid": ["Insira um UUID válido."]
                        },
                        "Situação desconhecida": {
                            "situacao": [
                                "Faça uma escolha válida. xx não é uma "
                                "das escolhas disponíveis."
                            ]
                        },
                        "Código de cargo não numérico": {
                            "vaga_escola__cargo_codigo": ["Informe um número."]
                        },
                    },
                ),
                404: RESPOSTA_PAGINA_INEXISTENTE,
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_escolha",
        summary="Criar escolha",
        description=(
            "Registra a escolha de um candidato em um concurso e grava o "
            "primeiro registro do histórico.\n\n"
            "Com a situação `escolha`, `tipo_vaga` e `vaga_escola_uuid` "
            "são obrigatórios, e a vaga perde uma unidade das restantes "
            "do tipo escolhido, sem ficar negativa. Nas demais situações "
            "a vaga é opcional e nada é descontado.\n\n"
            "O serviço não impede duas escolhas do mesmo candidato no "
            "mesmo concurso."
        ),
        request=EscolhaSerializer,
        examples=exemplos_requisicao(
            {
                "Escolha de vaga definitiva": EXEMPLO_NOVA_ESCOLHA,
                "Não escolha": EXEMPLO_NOVA_NAO_ESCOLHA,
            }
        ),
        responses=respostas(
            {
                201: resposta(
                    EscolhaDetalheSerializer,
                    "Escolha criada.",
                    {
                        "Escolha de vaga definitiva": EXEMPLO_ESCOLHA,
                        "Não escolha": EXEMPLO_NAO_ESCOLHA,
                    },
                ),
                400: RESPOSTA_DADOS_INVALIDOS,
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_escolha",
        summary="Detalhar escolha",
        description=(
            "Retorna uma escolha pelo UUID. A vaga vem só como UUID: os "
            "dados dela e o histórico estão na listagem.\n\n"
            f"{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_ESCOLHA, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_escolha",
        summary="Atualizar escolha",
        description=(
            "Substitui os dados da escolha. `candidato_uuid`, "
            "`concurso_uuid` e `situacao` são obrigatórios.\n\n"
            f"{AVISO_SEM_RECALCULO}\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=EscolhaSerializer,
        examples=exemplos_requisicao(
            {"Escolha de vaga definitiva": EXEMPLO_NOVA_ESCOLHA}
        ),
        responses=respostas(
            {
                200: RESPOSTA_ESCOLHA,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_escolha",
        summary="Atualizar escolha parcialmente",
        description=(
            "Altera apenas os campos enviados. Ao mudar a situação para "
            "`escolha`, a escolha precisa ter tipo de vaga e vaga, "
            "enviados agora ou já gravados.\n\n"
            f"{AVISO_SEM_RECALCULO}\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=EscolhaSerializer,
        examples=exemplos_requisicao(
            {"Passar para reconvocação": {"situacao": "reconvocacao"}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_ESCOLHA,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {
                        "Escolha sem tipo de vaga": ERRO_TIPO_DE_VAGA_AUSENTE,
                        "Vaga inexistente": ERRO_VAGA_INEXISTENTE,
                    },
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_escolha",
        summary="Excluir escolha",
        description=(
            "Exclui a escolha definitivamente, com o histórico dela. A "
            "vaga que tinha sido descontada não volta para as restantes."
            f"\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Escolha excluída."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
}
