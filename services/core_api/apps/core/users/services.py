from django.contrib.auth import authenticate
from pydantic import BaseModel, EmailStr
from django.utils import timezone
from datetime import timedelta
from .models import User, PasswordResetToken, SocialAccount
from .oauth_providers import OAuthUserInfo

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

        # Activate any pending organization invites for this email address
        from apps.core.organizations.models import Membership, PendingInvite
        pending = list(
            PendingInvite.objects.filter(
                email=data.email,
                is_accepted=False,
                expires_at__gt=timezone.now(),
            ).select_related('organization')
        )
        if pending:
            Membership.objects.bulk_create(
                [
                    Membership(
                        user=user,
                        organization=inv.organization,
                        role=inv.role,
                        status=Membership.StatusChoices.ACTIVE,
                    )
                    for inv in pending
                ],
                ignore_conflicts=True,
            )
            PendingInvite.objects.filter(id__in=[inv.id for inv in pending]).update(is_accepted=True)

        return user
    
    @staticmethod
    def login(data: LoginInput) -> User | None:
        user = authenticate(username=data.email, password=data.password)
        return user
    
class OAuthService:
    @staticmethod
    def authenticate(user_info: OAuthUserInfo) -> tuple[User, bool]:
        """Returns (user, is_new_user)"""
        try:
            social = SocialAccount.objects.select_related('user').get(
                provider=user_info.provider,
                social_id=user_info.social_id,
            )
            return social.user, False
        except SocialAccount.DoesNotExist:
            pass

        is_new = False
        try:
            user = User.objects.get(email=user_info.email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=user_info.email,
                password=None,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )
            is_new = True

        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified', 'updated_at'])

        SocialAccount.objects.create(
            user=user,
            provider=user_info.provider,
            social_id=user_info.social_id,
        )

        return user, is_new

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
        token_obj.user.save(update_fields=['password', 'updated_at'])
        token_obj.is_used = True
        token_obj.save(update_fields=['is_used'])

        return True, "Password reset successful"