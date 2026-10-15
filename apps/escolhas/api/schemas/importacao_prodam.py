"""Documentação OpenAPI da importação de escolhas da Prodam."""

from __future__ import annotations

from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema

from core.openapi import (
    CODIGO_CARGO_EXEMPLO,
    UUID_CANDIDATO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_interno,
    exemplos_requisicao,
    resposta,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from escola.api.schemas.escola import CODIGO_EOL_EXEMPLO
from escolhas.api.schemas.comuns import UUID_ESCOLHA_EXEMPLO
from escolhas.serializers import (
    EscolhasProdamImportacaoSerializer,
    ImportacaoProdamRespostaSerializer,
)

CPF_EXEMPLO = "12345678909"
CPF_DESCONHECIDO_EXEMPLO = "98765432100"

EXEMPLO_ITEM = {
    "cpf": CPF_EXEMPLO,
    "codigo_cargo": str(CODIGO_CARGO_EXEMPLO),
    "codigo_eol": CODIGO_EOL_EXEMPLO,
    "tipo_vaga": "D",
    "situacao": "ESCOLHA",
}

EXEMPLO_IMPORTACAO = {
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "escolhas": [
        EXEMPLO_ITEM,
        {
            "cpf": CPF_DESCONHECIDO_EXEMPLO,
            "codigo_cargo": str(CODIGO_CARGO_EXEMPLO),
            "codigo_eol": "",
            "tipo_vaga": None,
            "situacao": "NAO-ESCOLHA",
        },
    ],
}

EXEMPLO_ESCOLHA_IMPORTADA = {
    "uuid": UUID_ESCOLHA_EXEMPLO,
    "candidato_uuid": UUID_CANDIDATO_EXEMPLO,
    "situacao": "escolha",
}

EXEMPLO_RESULTADO = {
    "escolhas_criadas": 1,
    "escolhas": [EXEMPLO_ESCOLHA_IMPORTADA],
}

EXEMPLO_RESULTADO_SEM_NOVAS = {"escolhas_criadas": 0, "escolhas": []}

EXEMPLO_RESULTADO_COM_ERROS = {
    **EXEMPLO_RESULTADO,
    "erros": [
        {
            "index": 1,
            "cpf": CPF_DESCONHECIDO_EXEMPLO,
            "erro": "Candidato não encontrado",
        }
    ],
}

ERRO_IMPORTACAO_PRODAM = PolymorphicProxySerializer(
    component_name="ErroImportacaoDeEscolhas",
    serializers=[
        ImportacaoProdamRespostaSerializer,
        ErrosValidacaoSerializer,
    ],
    resource_type_field_name=None,
    many=False,
)

OPERACOES_IMPORTACAO_PRODAM = {
    "importacao_prodam": extend_schema(
        operation_id="importar_escolhas_prodam",
        summary="Importar escolhas da Prodam",
        description=(
            "Cria as escolhas de um processo de convocação a partir do "
            "resultado da Prodam. Em cada item, o candidato é localizado "
            "no MS-Candidatos pelo CPF, entre os habilitados convocados "
            "no processo, e a vaga, pelo código EOL e pelo código do "
            "cargo. Cada item é processado em separado, e uma escolha "
            "criada na situação `escolha` desconta a vaga.\n\n"
            "- **201**: nenhum item falhou. Itens de candidatos que já "
            "têm escolha no concurso são ignorados sem aviso, e por isso "
            "`escolhas_criadas` pode ser menor que a quantidade enviada, "
            "até zero.\n"
            "- **400** com `erros`: ao menos um item falhou. As escolhas "
            "dos demais itens **ficam criadas**, e `escolhas` as lista.\n\n"
            "Se o MS-Candidatos não responde, nenhum candidato é "
            "encontrado e todos os itens falham com `Candidato não "
            "encontrado`."
        ),
        request=EscolhasProdamImportacaoSerializer,
        examples=exemplos_requisicao(
            {"Uma escolha e uma não escolha": EXEMPLO_IMPORTACAO}
        ),
        responses=respostas(
            {
                201: resposta(
                    ImportacaoProdamRespostaSerializer,
                    "Importação sem falhas.",
                    {
                        "Uma escolha criada": EXEMPLO_RESULTADO,
                        "Todas já existiam": EXEMPLO_RESULTADO_SEM_NOVAS,
                    },
                ),
                400: resposta(
                    ERRO_IMPORTACAO_PRODAM,
                    (
                        "Corpo inválido, com os erros por campo, ou "
                        "importação em que ao menos um item falhou, com o "
                        "resultado e a lista `erros`."
                    ),
                    {
                        "Candidato não encontrado": (
                            EXEMPLO_RESULTADO_COM_ERROS
                        ),
                        "Campos inválidos": {
                            "concurso_uuid": ["Must be a valid UUID."],
                            "escolhas": {
                                "0": {
                                    "codigo_cargo": [
                                        "Este campo é obrigatório."
                                    ],
                                    "situacao": ["Este campo é obrigatório."],
                                }
                            },
                        },
                        "Lista vazia": {
                            "escolhas": ["Esta lista não pode estar vazia."]
                        },
                    },
                ),
                500: erro_interno(
                    "quando o `codigo_cargo` de algum item não é numérico"
                ),
            }
        ),
    ),
}
