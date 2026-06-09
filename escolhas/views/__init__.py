"""Módulo views/__init__."""
from .dre import DreViewSet
from .escola import EscolaViewSet
from .escolha import EscolhaViewSet
from .parametrizacao import ParametrizacaoViewSet
from .vagas_escolas import VagasEscolasViewSet

__all__ = [
    "EscolhaViewSet",
    "EscolaViewSet",
    "DreViewSet",
    "VagasEscolasViewSet",
    "ParametrizacaoViewSet",
]
