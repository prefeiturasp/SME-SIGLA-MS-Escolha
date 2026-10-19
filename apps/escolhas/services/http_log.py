"""Campos de log das chamadas HTTP aos outros microsserviços."""

from django.conf import settings


def mascarar_headers(headers: dict[str, str]) -> dict[str, str]:
    """Copia os headers e deixa só 3 caracteres na API key."""
    mascarados: dict[str, str] = {}
    for nome, valor in headers.items():
        if nome == settings.API_KEY_HEADER:
            mascarados[nome] = f"{valor[:3]}****"
        else:
            mascarados[nome] = valor
    return mascarados
