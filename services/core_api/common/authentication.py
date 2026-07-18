from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads access token from httpOnly cookie first, falls back to Authorization header.
    This allows Postman/API clients to still use Bearer tokens.
    """

    def authenticate(self, request):
        # Authorization header takes priority (Postman, mobile apps, etc.)
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
