import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory
from apps.core.organizations.models import Membership
from apps.workspace.activity.models import ActivityLog

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
    token = response.data['data']['tokens']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestActivity:
    def test_get_activity_log(self, auth_client, org):
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/activity/')
        assert response.status_code == 200

    def test_activity_unauthenticated(self, org):
        client = APIClient()
        response = client.get(f'/api/v1/organizations/{org.slug}/activity/')
        assert response.status_code == 401

    def test_activity_non_member(self, org):
        other_user = UserFactory()
        client = APIClient()
        client.post('/api/v1/auth/login/', {
            'email': other_user.email,
            'password': 'TestPass123!',
        }, format='json')
        response = client.get(f'/api/v1/organizations/{org.slug}/activity/')
        assert response.status_code == 401
