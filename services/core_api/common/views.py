import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from common.response import success_response, error_response

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return success_response({"status": "ok", "service": "core_api"}, message="Healthy")

@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    checks = {}

    # Database check
    try:
        connection.ensure_connection()
        checks['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks['database'] = 'error'

    # Redis check
    try:
        cache.set('health_check', 'ok', timeout=5)
        cache.get('health_check')
        checks['redis'] = 'ok'
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        checks['redis'] = 'error'

    all_ok = all(v == 'ok' for v in checks.values())

    if all_ok:
        return success_response(checks, message="Ready")
    return error_response(checks, message="Service not ready", status=503)
