"""Documentação OpenAPI das operações de escolas."""

from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from core.openapi import (
    AVISO_ROTA_HERDADA,
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
    RESPOSTA_PAGINA_INEXISTENTE,
    erro_interno,
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
from escola.api.schemas.dre import (
    CODIGO_DRE_EXEMPLO,
    EXEMPLO_DRE,
    NOME_DRE_EXEMPLO,
)
from escola.models import Escola
from escola.serializers import EscolaPaginadaSerializer, EscolaSerializer

TAG_ESCOLAS = "Escolas"

UUID_ESCOLA_EXEMPLO = "8d3b5f2a-7c1e-4a9d-b6f4-0e2c9a1d7b35"
CODIGO_EOL_EXEMPLO = "000191"
NOME_ESCOLA_EXEMPLO = "EMEF JARDIM DAS FLORES"
TIPO_UE_EXEMPLO = "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL"

CAMPO_OBRIGATORIO = ["Este campo é obrigatório."]

EXEMPLO_DADOS_ESCOLA = {
    "codigo_eol": CODIGO_EOL_EXEMPLO,
    "nome_oficial": NOME_ESCOLA_EXEMPLO,
    "nome_nao_oficial": "JARDIM DAS FLORES",
    "tipo_unidade_admin": "DIRETORIA REGIONAL DE EDUCACAO",
    "tipo_ue": TIPO_UE_EXEMPLO,
    "logradouro": "Rua das Flores",
    "numero": "123",
    "bairro": "VILA SONIA",
    "cep": "05624000",
    "distrito": "VILA SONIA",
    "sub_prefeitura": "BUTANTA",
    "nome_dre": NOME_DRE_EXEMPLO,
    "email": "emefjardimdasflores@exemplo.test",
    "telefone1": "1137420000",
    "telefone2": None,
    "ano_construcao": 1988,
    "propriedade": "PROPRIO",
    "capacidade_vagas_matutino": 420,
    "capacidade_vagas_vespertino": 420,
    "capacidade_vagas_noturno": 0,
    "capacidade_vagas_intermediario": 0,
    "capacidade_vagas_integral": 0,
    "capacidade_vagas_total": 840,
    "organizacao_parceira": False,
    "quantidade_de_funcionarios": 62,
    "status": "ATIVA",
}

EXEMPLO_ESCOLA = {
    "uuid": UUID_ESCOLA_EXEMPLO,
    "dre": EXEMPLO_DRE,
    **EXEMPLO_DADOS_ESCOLA,
    "criado_em": "2026-03-02T10:00:00-03:00",
    "atualizado_em": "2026-03-02T10:00:00-03:00",
}

ERRO_CAMPOS_AUSENTES = {
    campo: CAMPO_OBRIGATORIO
    for campo in (
        "codigo_eol",
        "nome_oficial",
        "tipo_unidade_admin",
        "tipo_ue",
        "logradouro",
        "numero",
        "bairro",
        "cep",
        "distrito",
        "sub_prefeitura",
        "nome_dre",
        "propriedade",
        "status",
    )
}

ERRO_FORMATO_INVALIDO = {
    "email": ["Insira um endereço de email válido."],
    "ano_construcao": ["Um número inteiro válido é exigido."],
}

PARAMETRO_UUID = parametro_uuid("UUID da escola.")

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="dre__codigo",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas as escolas da DRE com o código informado, por "
            f"exemplo `{CODIGO_DRE_EXEMPLO}`."
        ),
    ),
    OpenApiParameter(
        name="nome",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas as escolas cujo nome oficial contém o trecho "
            "informado."
        ),
    ),
    parametro_busca(
        "Busca por trecho do nome oficial, do código EOL, do nome da DRE "
        "ou do bairro."
    ),
    parametro_ordenacao(["criado_em", "nome_oficial"], "-criado_em"),
    PARAMETRO_PAGINA,
    PARAMETRO_TAMANHO_PAGINA,
]

RESPOSTA_ESCOLA = resposta(
    EscolaSerializer, "Escola.", {"Escola": EXEMPLO_ESCOLA}
)

RESPOSTA_NAO_ENCONTRADO = resposta_nao_encontrado(
    Escola,
    (
        "Escola inexistente, ou de um tipo de unidade desabilitado na "
        "parametrização."
    ),
)

RESPOSTA_DADOS_INVALIDOS = resposta(
    ErrosValidacaoSerializer,
    "Dados inválidos.",
    {
        "Campos ausentes": ERRO_CAMPOS_AUSENTES,
        "Formato inválido": ERRO_FORMATO_INVALIDO,
    },
)

OPERACOES_ESCOLAS = {
    "list": extend_schema(
        operation_id="listar_escolas",
        summary="Listar escolas",
        description=(
            "Retorna, em páginas, as escolas cujo tipo de unidade está "
            "habilitado na parametrização, da cadastrada mais "
            "recentemente para a mais antiga. Se nenhum tipo está "
            "habilitado, a lista vem vazia."
        ),
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    EscolaPaginadaSerializer,
                    "Página de escolas.",
                    {"Página": exemplo_pagina([EXEMPLO_ESCOLA])},
                ),
                404: RESPOSTA_PAGINA_INEXISTENTE,
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_escola",
        summary="Criar escola",
        description=(
            "Hoje esta rota não consegue criar uma escola: a DRE não pode "
            "ser informada no corpo, e um corpo válido termina em erro "
            "500. As escolas são carregadas da integração com a SME."
            f"\n\n{AVISO_ROTA_HERDADA}"
        ),
        request=EscolaSerializer,
        examples=exemplos_requisicao({"Nova escola": EXEMPLO_DADOS_ESCOLA}),
        responses=respostas(
            {
                400: RESPOSTA_DADOS_INVALIDOS,
                500: erro_interno(
                    "sempre que o corpo é válido, porque a escola ficaria "
                    "sem DRE"
                ),
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_escola",
        summary="Detalhar escola",
        description=(
            "Retorna uma escola pelo UUID, desde que o tipo de unidade "
            f"dela esteja habilitado.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_ESCOLA, 404: RESPOSTA_NAO_ENCONTRADO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_escola",
        summary="Atualizar escola",
        description=(
            "Substitui os dados cadastrais da escola. A DRE não muda."
            f"\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=EscolaSerializer,
        examples=exemplos_requisicao(
            {"Dados da escola": EXEMPLO_DADOS_ESCOLA}
        ),
        responses=respostas(
            {
                200: RESPOSTA_ESCOLA,
                400: RESPOSTA_DADOS_INVALIDOS,
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_escola",
        summary="Atualizar escola parcialmente",
        description=(
            f"Altera apenas os campos enviados.\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        request=EscolaSerializer,
        examples=exemplos_requisicao(
            {"Corrigir o telefone": {"telefone1": "1137420000"}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_ESCOLA,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados inválidos.",
                    {"Formato inválido": ERRO_FORMATO_INVALIDO},
                ),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_escola",
        summary="Excluir escola",
        description=(
            "Exclui a escola definitivamente, junto com as vagas dela. As "
            "escolhas feitas nessas vagas continuam, mas ficam sem vaga."
            f"\n\n{AVISO_ROTA_HERDADA}"
        ),
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Escola excluída."),
                404: RESPOSTA_NAO_ENCONTRADO,
            }
        ),
    ),
}
