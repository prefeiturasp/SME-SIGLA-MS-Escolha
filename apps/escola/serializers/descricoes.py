"""Descrições dos campos de DRE e de escola na documentação da API."""

DESCRICOES_DRE = {
    "uuid": {"help_text": "Identificador da DRE."},
    "codigo": {"help_text": "Código da DRE na SME, por exemplo `108100`."},
    "nome": {"help_text": "Nome da DRE."},
    "sigla": {"help_text": "Sigla da DRE, por exemplo `DRE - BT`."},
}

DESCRICOES_ESCOLA = {
    "uuid": {"help_text": "Identificador da escola."},
    "codigo_eol": {
        "help_text": (
            "Código EOL da escola, com 6 dígitos. É por ele que as vagas "
            "são vinculadas à escola."
        )
    },
    "nome_oficial": {"help_text": "Nome oficial da escola."},
    "nome_nao_oficial": {"help_text": "Nome pelo qual a escola é conhecida."},
    "tipo_unidade_admin": {
        "help_text": (
            "Tipo da unidade administrativa a que a escola pertence, por "
            "exemplo `DIRETORIA REGIONAL DE EDUCACAO`."
        )
    },
    "tipo_ue": {
        "help_text": (
            "Tipo de unidade escolar, por exemplo `ESCOLA MUNICIPAL DE "
            "ENSINO FUNDAMENTAL`. A escola só aparece na API se o tipo "
            "estiver habilitado na parametrização."
        )
    },
    "logradouro": {"help_text": "Logradouro do endereço."},
    "numero": {"help_text": "Número do endereço."},
    "bairro": {"help_text": "Bairro do endereço."},
    "cep": {"help_text": "CEP do endereço, só com dígitos."},
    "distrito": {"help_text": "Distrito do município em que a escola fica."},
    "sub_prefeitura": {"help_text": "Subprefeitura em que a escola fica."},
    "nome_dre": {
        "help_text": "Nome da DRE como consta no cadastro da escola na SME."
    },
    "email": {"help_text": "E-mail de contato da escola."},
    "telefone1": {"help_text": "Telefone principal da escola."},
    "telefone2": {"help_text": "Telefone alternativo da escola."},
    "ano_construcao": {"help_text": "Ano de construção do prédio."},
    "propriedade": {
        "help_text": (
            "Situação do imóvel no cadastro da SME, por exemplo `PROPRIO`. "
            "Escolas importadas da SME vêm com `DESCONHECIDO`."
        )
    },
    "capacidade_vagas_matutino": {
        "help_text": "Capacidade de alunos no turno matutino."
    },
    "capacidade_vagas_vespertino": {
        "help_text": "Capacidade de alunos no turno vespertino."
    },
    "capacidade_vagas_noturno": {
        "help_text": "Capacidade de alunos no turno noturno."
    },
    "capacidade_vagas_intermediario": {
        "help_text": "Capacidade de alunos no turno intermediário."
    },
    "capacidade_vagas_integral": {
        "help_text": "Capacidade de alunos em período integral."
    },
    "capacidade_vagas_total": {
        "help_text": "Capacidade total de alunos da escola."
    },
    "organizacao_parceira": {
        "help_text": (
            "Indica se a escola é mantida por uma organização parceira."
        )
    },
    "quantidade_de_funcionarios": {
        "help_text": "Quantidade de funcionários da escola."
    },
    "status": {
        "help_text": (
            "Situação da escola no cadastro da SME, em texto livre, por "
            "exemplo `ATIVA`."
        )
    },
    "codigo_integracao": {
        "help_text": (
            "Código da escola na API de integração da SME, ou nulo se "
            "ainda não foi obtido."
        )
    },
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última alteração do registro."
    },
}
