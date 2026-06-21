import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tests.factories import UserFactory

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': user.email,
        'password': 'TestPass123!',
    }, format='json')
    token = response.data['data']['tokens']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client):
        response = client.post('/api/v1/auth/register/', {
            'email': 'newuser@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
        }, format='json')
        assert response.status_code == 201
        assert response.data['success'] == True

    def test_register_duplicate_email(self, client, user):
        response = client.post('/api/v1/auth/register/', {
            'email': user.email,
            'password': 'StrongPass123!',
        }, format='json')
        assert response.status_code == 400
        assert response.data['success'] == False

    def test_register_missing_email(self, client):
        response = client.post('/api/v1/auth/register/', {
            'password': 'StrongPass123!',
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
        assert response.data['success'] == True
        assert 'access_token' in response.data['data']['tokens']

    def test_login_wrong_password(self, client, user):
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'wrongpassword',
        }, format='json')
        assert response.status_code == 401
        assert response.data['success'] == False

    def test_login_wrong_email(self, client):
        response = client.post('/api/v1/auth/login/', {
            'email': 'notexist@test.com',
            'password': 'TestPass123!',
        }, format='json')
        assert response.status_code == 401

@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, auth_client, client, user):
        refresh_response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        refresh_token = refresh_response.data['data']['tokens']['refresh_token']

        response = auth_client.post('/api/v1/auth/logout/', {
            'refresh_token': refresh_token,
        }, format='json')
        assert response.status_code == 200
        assert response.data['success'] == True

    def test_logout_without_auth(self, client):
        response = client.post('/api/v1/auth/logout/', {
            'refresh_token': 'fake-token',
        }, format='json')
        assert response.status_code == 401
