import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory

@pytest.fixture
def user(db):
    return UserFactory(first_name='Awais', last_name='Amin')

@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': user.email,
        'password': 'TestPass123!',
    }, format='json')
    token = response.data['data']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, auth_client, user):
        response = auth_client.get('/api/v1/auth/profile/')
        assert response.status_code == 200
        assert response.data['data']['email'] == user.email
        assert response.data['data']['first_name'] == 'Awais'

    def test_update_profile(self, auth_client):
        response = auth_client.patch('/api/v1/auth/profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['first_name'] == 'Updated'

    def test_update_profile_empty_first_name(self, auth_client):
        response = auth_client.patch('/api/v1/auth/profile/', {
            'first_name': '   ',
        }, format='json')
        assert response.status_code == 400

    def test_profile_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/v1/auth/profile/')
        assert response.status_code == 401

@pytest.mark.django_db
class TestChangePassword:
    def test_change_password_success(self, auth_client):
        response = auth_client.post('/api/v1/auth/profile/change-password/', {
            'current_password': 'TestPass123!',
            'new_password': 'NewSecurePass456@',
        }, format='json')
        assert response.status_code == 200

    def test_change_password_wrong_current(self, auth_client):
        response = auth_client.post('/api/v1/auth/profile/change-password/', {
            'current_password': 'WrongPass!',
            'new_password': 'NewSecurePass456@',
        }, format='json')
        assert response.status_code == 400

    def test_change_password_weak_new_password(self, auth_client):
        response = auth_client.post('/api/v1/auth/profile/change-password/', {
            'current_password': 'TestPass123!',
            'new_password': '123',
        }, format='json')
        assert response.status_code == 400

    def test_change_password_unauthenticated(self):
        client = APIClient()
        response = client.post('/api/v1/auth/profile/change-password/', {
            'current_password': 'TestPass123!',
            'new_password': 'NewSecurePass456@',
        }, format='json')
        assert response.status_code == 401
