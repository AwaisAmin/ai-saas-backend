import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client):
        response = client.post('/api/v1/auth/register/', {
            'email': 'newuser@example.com',
            'password': 'SecurePass456@',
            'first_name': 'John',
            'last_name': 'Doe',
        }, format='json')
        assert response.status_code == 201
        assert response.data['data']['email'] == 'newuser@example.com'

    def test_register_duplicate_email(self, client, user):
        response = client.post('/api/v1/auth/register/', {
            'email': user.email,
            'password': 'SecurePass456@',
        }, format='json')
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        response = client.post('/api/v1/auth/register/', {
            'email': 'not-an-email',
            'password': 'SecurePass456@',
        }, format='json')
        assert response.status_code == 400

@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, user):
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        assert response.status_code == 200
        assert 'access_token' in response.data['data']
        assert 'access_token' in response.cookies
        assert response.cookies['access_token']['httponly']
        assert 'refresh_token' in response.cookies
        assert response.cookies['refresh_token']['httponly']

    def test_login_returns_user_and_organizations(self, client, user):
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        assert 'user' in response.data['data']
        assert 'organizations' in response.data['data']

    def test_login_wrong_password(self, client, user):
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'WrongPass!',
        }, format='json')
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post('/api/v1/auth/login/', {
            'email': 'nobody@example.com',
            'password': 'TestPass123!',
        }, format='json')
        assert response.status_code == 401

@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, client, user):
        login = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        access_token = login.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = client.post('/api/v1/auth/logout/')
        assert response.status_code == 200

    def test_logout_clears_cookies(self, client, user):
        login = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        access_token = login.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = client.post('/api/v1/auth/logout/')
        assert response.cookies['refresh_token'].value == ''
        assert response.cookies['access_token'].value == ''

    def test_logout_unauthenticated(self, client):
        response = client.post('/api/v1/auth/logout/')
        assert response.status_code == 401

@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_success(self, client, user):
        client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')

        response = client.post('/api/v1/auth/token/refresh/')
        assert response.status_code == 200
        assert 'access_token' in response.cookies
        assert response.cookies['access_token']['httponly']

    def test_refresh_without_cookie(self, client):
        response = client.post('/api/v1/auth/token/refresh/')
        assert response.status_code == 401

@pytest.mark.django_db
class TestResendVerification:
    def test_resend_unverified_user(self, client, user):
        user.is_verified = False
        user.save()
        response = client.post('/api/v1/auth/resend-verification/', {
            'email': user.email,
        }, format='json')
        assert response.status_code == 200

    def test_resend_verified_user(self, client, user):
        user.is_verified = True
        user.save()
        response = client.post('/api/v1/auth/resend-verification/', {
            'email': user.email,
        }, format='json')
        assert response.status_code == 200

    def test_resend_nonexistent_email(self, client):
        response = client.post('/api/v1/auth/resend-verification/', {
            'email': 'ghost@example.com',
        }, format='json')
        assert response.status_code == 200
