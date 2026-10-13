"""Serializers do app escola."""

from .dre import DrePaginadaSerializer, DreSerializer
from .escola import (
    EscolaListSerializer,
    EscolaPaginadaSerializer,
    EscolaSelectSerializer,
    EscolaSerializer,
)

__all__ = [
    "DreSerializer",
    "DrePaginadaSerializer",
    "EscolaSerializer",
    "EscolaPaginadaSerializer",
    "EscolaSelectSerializer",
    "EscolaListSerializer",
]
