import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data if response.data else None
        message = "An error occurred"

        if isinstance(exc, Throttled):
            wait = int(exc.wait) if exc.wait else 60
            if wait < 60:
                message = f"Too many requests. Please wait {wait} seconds."
            elif wait < 3600:
                message = f"Too many requests. Please try again in {wait // 60} minutes."
            else:
                message = "Too many requests. Please try again later."
            return Response({
                "success": False,
                "message": message,
                "data": None,
                "errors": None,
            }, status=response.status_code)

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
