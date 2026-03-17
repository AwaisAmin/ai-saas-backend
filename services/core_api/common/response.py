from rest_framework.response import Response

def success_response(data=None, message="Success", status=200):
    return Response({
        "success": True,
        "message": message,
        "data": data,
        "errors": None,
    }, status=status)

def error_response(errors=None, message="Something went wrong", status=400):
    return Response({
        "success": False,
        "message": message,
        "data": None,
        "errors": errors,
    }, status=status)

def format_errors(errors: dict) -> list:
    result = []
    for field, messages in errors.items():
        message = messages[0] if isinstance(messages, list) else str(messages)
        result.append({
            "field": field,
            "message": message,
            "code": field.upper() + "_ERROR"
        })
    return result
