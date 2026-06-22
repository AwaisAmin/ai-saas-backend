import uuid                       
from django.conf import settings     

from rest_framework.views import APIView                          
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from common.response import success_response, error_response, format_errors  

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .services import AuthService, LoginInput, RegisterInput, PasswordResetService, PasswordResetInput, PasswordResetConfirmInput
from .models import User
from .tasks import send_welcome_email, send_verification_email, send_password_reset_email

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")
        
        data = RegisterInput(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name',''),
            last_name=serializer.validated_data.get('last_name',''),
        )
        user = AuthService.register(data)
        send_welcome_email.delay(user.email, user.first_name)
        send_verification_email.delay(
            user.email,
            user.first_name,
            str(user.verification_token),
        )

        return success_response(
            data=UserSerializer(user).data,
            message="Account created successfully. Please verify your email.",
            status=201
        )
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")
        
        data = LoginInput(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        user = AuthService.login(data)

        if user is None:
            return error_response(message="Invalid email or password", status=401)
        
        refresh = RefreshToken.for_user(user)
        response = success_response(
            data={
                "user": UserSerializer(user).data,
                "tokens": {
                    "access_token": str(refresh.access_token),
                }
            },
            message="Login successfully"
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax" if settings.DEBUG else "Strict",
            max_age=60 * 60 * 24 * 7,
            path="/api/v1/auth/",
        )
        return response
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return error_response(message="Refresh token required")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken):
            pass

        response = success_response(message="Logged out successfully")
        response.delete_cookie(
            key="refresh_token",
            path="/api/v1/auth/",
        )
        return response
    
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return error_response(message="Refresh token not found", status=401)

        try:
            token = RefreshToken(refresh_token)
            return success_response(
                data={"access_token": str(token.access_token)},
                message="Token refreshed successfully",
            )
        except (TokenError, InvalidToken):
            return error_response(message="Invalid or expired refresh token", status=401)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        token = request.GET.get('token')
        if not token:
            return error_response(message="Token is required", status=400)

        try:
            user = User.objects.get(verification_token=token)
        except User.DoesNotExist:
            return error_response(message="Invalid or expired token", status=400)

        if user.is_verified:
            return success_response(message="Email already verified")
        
        user.is_verified = True
        user.verification_token = uuid.uuid4()
        user.save(update_fields=['is_verified', 'verification_token', 'updated_at'])

        return success_response(message="Email verified successfully")

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        email = request.data.get("email")
        if not email:
            return error_response(message="Email is required", status=400)

        token = PasswordResetService.create_token(PasswordResetInput(email=email))

        if token:
            send_password_reset_email.delay(token.user.email, token.user.first_name, str(token.token))

        return success_response(message="If this email exists, a reset link has been sent.")

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return error_response(message="token and new_password are required", status=400)

        success, message = PasswordResetService.reset_password(
            PasswordResetConfirmInput(token=token, new_password=new_password)
        )

        if not success:
            return error_response(message=message, status=400)

        return success_response(message=message)