"""Services do app vagas_escolas."""

from .vagas_escolas import (
    adicionar_vagas_ao_lote_por_processo,
    atualizar_vagas_utilizadas_por_processo,
    criar_vagas_em_lote,
    processar_criacao_vagas_lote,
)

__all__ = [
    "criar_vagas_em_lote",
    "processar_criacao_vagas_lote",
    "adicionar_vagas_ao_lote_por_processo",
    "atualizar_vagas_utilizadas_por_processo",
]
