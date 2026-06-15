"""Módulo middleware."""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from typing import Any

_thread_locals = threading.local()
logger = logging.getLogger("django.request_logger")


def get_correlation_id() -> Any:
    """Retorna correlation id."""
    return getattr(_thread_locals, "correlation_id", None)


logger = logging.getLogger("django.request_logger")


class CorrelationIdMiddleware:
    """Representa CorrelationIdMiddleware."""

    def __init__(self, get_response: Any) -> None:
        """Inicializa a instância com os parâmetros informados."""
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        """Call middleware para adicionar correlation id às requisições."""
        start_time = time.perf_counter()
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        _thread_locals.correlation_id = cid
        payload = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.content_type == "application/json" and request.body:
                    payload = json.loads(request.body)
                else:
                    payload = request.POST.dict() or request.body.decode(
                        "utf-8", errors="replace"
                    )
            except Exception:
                payload = "<erro_ao_ler_payload>"
        response = self.get_response(request)
        if request.method != "OPTIONS":
            duration = (time.perf_counter() - start_time) * 1000
            extra_data = {
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": round(duration, 2),
                "payload": payload,
                "user": str(request.user)
                if hasattr(request, "user")
                else "Anonymous",
            }
            logger.info(f"{request.method} {request.path}", extra=extra_data)
        response["X-Correlation-ID"] = cid
        return response
