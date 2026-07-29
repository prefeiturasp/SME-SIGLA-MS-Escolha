"""Fixtures compartilhadas entre os apps."""

from __future__ import annotations

import uuid

import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def _sem_sigla_sdk_middleware(settings):
    """Remove middlewares do sigla_sdk ausentes no pacote de testes."""
    settings.MIDDLEWARE = [
        middleware
        for middleware in settings.MIDDLEWARE
        if not middleware.startswith("sigla_sdk.middlewares.")
    ]


@pytest.fixture
def api_client():
    """Cliente API sem autenticação."""
    return APIClient()


@pytest.fixture
def fake_uuid():
    """UUID aleatório para cenários de recurso inexistente."""
    return uuid.uuid4()
