"""Serializers do app escola."""

from .dre import DreSerializer
from .escola import (
    EscolaListSerializer,
    EscolaSelectSerializer,
    EscolaSerializer,
)

__all__ = [
    "DreSerializer",
    "EscolaSerializer",
    "EscolaSelectSerializer",
    "EscolaListSerializer",
]
