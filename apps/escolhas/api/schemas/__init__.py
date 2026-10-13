"""Documentação OpenAPI das operações de escolhas e de extração de dados."""

from .comuns import TAG_ESCOLHAS
from .consultas import OPERACOES_CONSULTAS
from .escolha import OPERACOES_CADASTRO
from .extracao_dados import OPERACOES_EXTRACAO_DADOS, TAG_EXTRACAO_DADOS
from .importacao_prodam import OPERACOES_IMPORTACAO_PRODAM

OPERACOES_ESCOLHAS = {
    **OPERACOES_CADASTRO,
    **OPERACOES_CONSULTAS,
    **OPERACOES_IMPORTACAO_PRODAM,
}

__all__ = [
    "OPERACOES_ESCOLHAS",
    "OPERACOES_EXTRACAO_DADOS",
    "TAG_ESCOLHAS",
    "TAG_EXTRACAO_DADOS",
]
