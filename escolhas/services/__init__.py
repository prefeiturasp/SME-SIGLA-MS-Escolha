"""Módulo services/__init__."""

from .candidato_api import CandidatoAPIService
from .concurso_api import ConcursoAPIService
from .sme_integration import (
    buscar_dados_escola_por_eol,
    buscar_dres_de_smeintegracao,
    buscar_ues_codigos_por_dre,
)
from .vagas_escolas import (
    criar_vagas_em_lote,
    processar_criacao_vagas_lote,
)
