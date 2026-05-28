from .base import BaseModel
from .dre import Dre
from .escola import Escola
from .escolha import Escolha
from .historico_escolha import HistoricoEscolha
from .parametrizacao import Parametrizacao
from .vagas_escolas import VagasEscolas
from .vagas_lote import VagasEscolasLote

__all__ = [
    "BaseModel",
    "Dre",
    "Escola",
    "Escolha",
    "VagasEscolas",
    "VagasEscolasLote",
    "HistoricoEscolha",
    "Parametrizacao",
]
