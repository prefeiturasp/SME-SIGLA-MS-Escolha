"""Descrições dos campos de escolha na documentação da API."""

DESCRICOES_ESCOLHA = {
    "uuid": {"help_text": "Identificador da escolha."},
    "candidato_uuid": {
        "help_text": (
            "UUID do habilitado no MS-Candidatos, isto é, do vínculo do "
            "candidato com o concurso."
        )
    },
    "concurso_uuid": {"help_text": "UUID do concurso no MS-Concursos."},
    "processo_uuid": {
        "help_text": (
            "UUID do processo de convocação em que a escolha foi feita, "
            "ou nulo se não foi informado."
        )
    },
    "situacao": {"help_text": "Situação da escolha."},
    "tipo_vaga": {
        "help_text": (
            "Tipo da vaga escolhida. Obrigatório quando a situação é "
            "`escolha`."
        )
    },
    "e_retardatario": {
        "help_text": (
            "Indica se o candidato escolheu fora do horário previsto. "
            "Vale `false` quando não é enviado."
        )
    },
    "vaga_escola": {
        "help_text": "UUID da vaga escolhida, ou nulo se não há vaga."
    },
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}

DESCRICOES_HISTORICO = {
    "uuid": {"help_text": "Identificador do registro de histórico."},
    "situacao_anterior": {
        "help_text": (
            "Situação que a escolha tinha antes, ou nulo no registro de "
            "criação."
        )
    },
    "situacao_nova": {"help_text": "Situação que a escolha passou a ter."},
    "criado_em": {"help_text": "Data e hora da mudança de situação."},
}
