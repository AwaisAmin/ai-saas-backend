import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory
from apps.core.organizations.models import Membership

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def org(db):
    return OrganizationFactory()

@pytest.fixture
def membership(db, user, org):
    return MembershipFactory(user=user, organization=org, role=Membership.RoleChoices.OWNER)

@pytest.fixture
def auth_client(user, membership):
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': user.email,
        'password': 'TestPass123!',
    }, format='json')
    token = response.data['data']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestSubscriptions:
    def test_get_subscription(self, auth_client, org):
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/subscription/')
        assert response.status_code == 200
        assert response.data['data']['subscription']['plan'] == 'free'

    def test_get_subscription_includes_limits(self, auth_client, org):
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/subscription/')
        assert response.status_code == 200
        data = response.data['data']
        assert 'limits' in data
        assert 'usage' in data
        assert data['limits']['max_projects'] == 3
        assert data['limits']['max_members'] == 5

    def test_get_subscription_unauthenticated(self, org):
        client = APIClient()
        response = client.get(f'/api/v1/organizations/{org.slug}/subscription/')
        assert response.status_code == 401

    def test_get_subscription_non_member(self, org):
        other_user = UserFactory()
        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': other_user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')
        response = client.get(f'/api/v1/organizations/{org.slug}/subscription/')
        assert response.status_code == 403
