import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from tests.factories import UserFactory
from apps.core.users.models import PasswordResetToken

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.mark.django_db
class TestPasswordReset:
    def test_request_reset_existing_email(self, user):
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/', {
            'email': user.email,
        }, format='json')
        assert response.status_code == 200
        assert 'If this email exists' in response.data['message']

    def test_request_reset_nonexistent_email(self):
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/', {
            'email': 'ghost@test.com',
        }, format='json')
        assert response.status_code == 200
        assert 'If this email exists' in response.data['message']

    def test_request_reset_missing_email(self):
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/', {}, format='json')
        assert response.status_code == 400

    def test_confirm_valid_token(self, user):
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/confirm/', {
            'token': str(token.token),
            'new_password': 'NewPass456!',
        }, format='json')
        assert response.status_code == 200
        token.refresh_from_db()
        assert token.is_used is True

    def test_confirm_invalid_token(self):
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/confirm/', {
            'token': '00000000-0000-0000-0000-000000000000',
            'new_password': 'NewPass456!',
        }, format='json')
        assert response.status_code == 400

    def test_confirm_expired_token(self, user):
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/confirm/', {
            'token': str(token.token),
            'new_password': 'NewPass456!',
        }, format='json')
        assert response.status_code == 400

    def test_confirm_used_token(self, user):
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1),
            is_used=True,
        )
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/confirm/', {
            'token': str(token.token),
            'new_password': 'NewPass456!',
        }, format='json')
        assert response.status_code == 400

    def test_confirm_missing_fields(self):
        client = APIClient()
        response = client.post('/api/v1/auth/password-reset/confirm/', {}, format='json')
        assert response.status_code == 400

    def test_password_actually_changed(self, user):
        token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        client = APIClient()
        client.post('/api/v1/auth/password-reset/confirm/', {
            'token': str(token.token),
            'new_password': 'BrandNew789!',
        }, format='json')
        login_response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'BrandNew789!',
        }, format='json')
        assert login_response.status_code == 200
