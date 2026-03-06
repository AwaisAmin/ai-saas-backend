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