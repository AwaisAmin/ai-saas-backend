import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data if response.data else None
        message = "An error occurred"

        if isinstance(errors, dict) and "detail" in errors:
            message = str(errors["detail"])
            errors = None

        return Response({
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        }, status=response.status_code)

    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return Response({
        "success": False,
        "message": "Something went wrong",
        "data": None,
        "errors": None,
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
