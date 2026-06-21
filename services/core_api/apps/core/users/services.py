from django.contrib.auth import authenticate
from pydantic import BaseModel, EmailStr
from django.utils import timezone
from datetime import timedelta
from .models import User, PasswordResetToken

class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class PasswordResetInput(BaseModel):
    email: EmailStr

class PasswordResetConfirmInput(BaseModel):
    token: str
    new_password: str    

class AuthService:
    @staticmethod
    def register(data: RegisterInput) -> User:
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return user
    
    @staticmethod
    def login(data: LoginInput) -> User | None:
        user = authenticate(username=data.email, password=data.password)
        return user
    
class PasswordResetService:
    @staticmethod
    def create_token(data: PasswordResetInput):
        try:
            user = User.objects.get(email=data.email, is_active=True)
        except User.DoesNotExist:
            return None

        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        return token

    @staticmethod
    def reset_password(data: PasswordResetConfirmInput) -> tuple[bool, str]:
        try:
            token_obj = PasswordResetToken.objects.select_related('user').get(
                token=data.token
            )
        except PasswordResetToken.DoesNotExist:
            return False, "Invalid token"

        if not token_obj.is_valid():
            return False, "Token expired or already used"

        token_obj.user.set_password(data.new_password)
        token_obj.user.save()
        token_obj.is_used = True
        token_obj.save()

        return True, "Password reset successful"