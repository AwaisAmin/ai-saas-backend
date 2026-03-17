from django.contrib.auth import authenticate
from pydantic import BaseModel, EmailStr
from .models import User

class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""

class LoginInput(BaseModel):
    email: EmailStr
    password: str

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