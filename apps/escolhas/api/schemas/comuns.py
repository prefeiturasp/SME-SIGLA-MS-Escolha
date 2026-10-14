"""Blocos de documentação comuns às operações de escolhas."""

from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from core.openapi import (
    UUID_CANDIDATO_2_EXEMPLO,
    UUID_CANDIDATO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_interno,
)
from vagas_escolas.api.schemas import EXEMPLO_VAGA, UUID_VAGA_EXEMPLO

TAG_ESCOLHAS = "Escolhas"

UUID_ESCOLHA_EXEMPLO = "40928753-183f-4eee-bdf1-04baaa9b4265"
UUID_ESCOLHA_2_EXEMPLO = "d9d5eb3d-eca5-43a4-8e9f-4918833c4162"
UUID_HISTORICO_EXEMPLO = "c7b1fdc0-9b6d-4900-a752-30bfb556a51c"

AVISO_UUID_MALFORMADO = (
    "Os UUIDs do corpo não têm o formato validado: um valor malformado "
    "resulta em erro 500."
)

AVISO_CONSULTA_POR_POST = (
    "A consulta usa POST para receber a lista no corpo e não altera nada."
)

EXEMPLO_ESCOLHA = {
    "uuid": UUID_ESCOLHA_EXEMPLO,
    "candidato_uuid": UUID_CANDIDATO_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "situacao": "escolha",
    "tipo_vaga": "definitiva",
    "e_retardatario": False,
    "vaga_escola": UUID_VAGA_EXEMPLO,
    "criado_em": "2026-03-10T09:15:00-03:00",
    "atualizado_em": "2026-03-10T09:15:00-03:00",
    "vaga_escola_uuid": UUID_VAGA_EXEMPLO,
}

EXEMPLO_NAO_ESCOLHA = {
    "uuid": UUID_ESCOLHA_2_EXEMPLO,
    "candidato_uuid": UUID_CANDIDATO_2_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "processo_uuid": None,
    "situacao": "nao-escolha",
    "tipo_vaga": None,
    "e_retardatario": False,
    "vaga_escola": None,
    "criado_em": "2026-03-10T09:20:00-03:00",
    "atualizado_em": "2026-03-10T09:20:00-03:00",
    "vaga_escola_uuid": None,
}

EXEMPLO_ESCOLHA_LISTADA = {
    "uuid": UUID_ESCOLHA_EXEMPLO,
    "candidato_uuid": UUID_CANDIDATO_EXEMPLO,
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "situacao": "escolha",
    "tipo_vaga": "definitiva",
    "e_retardatario": False,
    "vaga_escola_uuid": UUID_VAGA_EXEMPLO,
    "vaga_escola": {**EXEMPLO_VAGA, "vagas_definitivas_restantes": 2},
    "historico": [
        {
            "uuid": UUID_HISTORICO_EXEMPLO,
            "situacao_anterior": None,
            "situacao_nova": "escolha",
            "criado_em": "2026-03-10T09:15:00-03:00",
        }
    ],
    "criado_em": "2026-03-10T09:15:00-03:00",
    "atualizado_em": "2026-03-10T09:15:00-03:00",
}

PARAMETRO_FIELDS = OpenApiParameter(
    name="fields",
    type=OpenApiTypes.STR,
    description=(
        "Nomes dos campos a devolver, separados por vírgula, por exemplo "
        "`uuid,candidato_uuid`. Os demais campos saem de cada escolha da "
        "resposta, e nomes desconhecidos são ignorados."
    ),
)

ERRO_INTERNO_UUID_MALFORMADO = erro_interno(
    "quando algum UUID do corpo é malformado"
)
