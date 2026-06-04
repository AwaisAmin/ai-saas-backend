from .models import User
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from common.response import success_response, error_response, format_errors
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .services import AuthService, LoginInput, RegisterInput
from .tasks import send_welcome_email, send_verification_email

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
        return success_response(
            data={
                "user": UserSerializer(user).data,
                "tokens": {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }
            },
            message="Login successfully"
        )
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return error_response(message="Refresh token required")
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        return success_response(message="Logged out successfully")
    
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return success_response(
                data={"access_token": response.data['access']},
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
        user.save(update_fields=['is_verified', 'updated_at'])

        return success_response(message="Email verified successfully")
