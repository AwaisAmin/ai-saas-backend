from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads access token from httpOnly cookie first, falls back to Authorization header.
    When authenticating via cookie, CSRF is enforced for extra security.
    Postman/API clients can still use Bearer tokens (no CSRF required).
    """

    def authenticate(self, request):
        # Authorization header takes priority (Postman, mobile apps, etc.)
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        # Cookie-based auth — enforce CSRF
        self._enforce_csrf(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def _enforce_csrf(self, request):
        check = CSRFCheck(request)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f"CSRF check failed: {reason}")
