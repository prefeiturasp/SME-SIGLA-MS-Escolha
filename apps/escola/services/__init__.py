"""Services do app escola."""

from .sme_integration import (
    buscar_dados_escola_por_eol,
    buscar_dres_de_smeintegracao,
    buscar_ues_codigos_por_dre,
)

__all__ = [
    "buscar_dados_escola_por_eol",
    "buscar_dres_de_smeintegracao",
    "buscar_ues_codigos_por_dre",
]
