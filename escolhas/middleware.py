import logging
import time
import json
import uuid
import threading

_thread_locals = threading.local()
logger = logging.getLogger('django.request_logger')


def get_correlation_id():
    return getattr(_thread_locals, 'correlation_id', None)

logger = logging.getLogger('django.request_logger')

class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()
        cid = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        _thread_locals.correlation_id = cid

        # --- EXTRAÇÃO DO PAYLOAD ---
        payload = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Verificamos se é JSON para tentar parsear
                if request.content_type == 'application/json' and request.body:
                    payload = json.loads(request.body)
                else:
                    # Para outros tipos (form-data), pegamos o que for possível
                    payload = request.POST.dict() or request.body.decode('utf-8', errors='replace')
            except Exception:
                payload = "<erro_ao_ler_payload>"

        response = self.get_response(request)

        if request.method != 'OPTIONS':
            duration = (time.perf_counter() - start_time) * 1000

            extra_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration, 2),
                'payload': payload,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous'
            }
            logger.info(f"{request.method} {request.path}", extra=extra_data)

        response['X-Correlation-ID'] = cid
        return response