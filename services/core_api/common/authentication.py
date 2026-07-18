from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied


class CookieJWTAuthentication(JWTAuthentication):
    """
    - Authorization header present → header auth, no CSRF (Postman/mobile)
    - No header, access_token cookie present → cookie auth + CSRF enforced (browser)
    """

    def authenticate(self, request):
        # Authorization header takes priority — no CSRF needed (Postman, mobile apps)
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        # Cookie-based auth (browser) — enforce CSRF
        self._enforce_csrf(request)

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def _enforce_csrf(self, request):
        check = CSRFCheck(request)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f"CSRF check failed: {reason}")
