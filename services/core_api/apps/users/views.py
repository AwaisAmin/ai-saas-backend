from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from common.response import success_response, error_response, format_errors
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .services import AuthService, LoginInput, RegisterInput

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

        return success_response(
            data=UserSerializer(user).data,
            message="Account created successfully",
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