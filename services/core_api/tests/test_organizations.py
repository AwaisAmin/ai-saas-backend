import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory

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

@pytest.fixture
def org_with_owner(user):
    org = OrganizationFactory()
    MembershipFactory(user=user, organization=org, role='owner')
    return org

@pytest.mark.django_db
class TestOrganizations:
    def test_create_org_success(self, auth_client):
        response = auth_client.post('/api/v1/organizations/', {
            'name': 'Test Org',
            'slug': 'test-org',
        }, format='json')
        assert response.status_code == 201
        assert response.data['success'] == True

    def test_create_org_unauthenticated(self, client):
        response = client.post('/api/v1/organizations/', {
            'name': 'Test Org',
            'slug': 'test-org',
        }, format='json')
        assert response.status_code == 401

    def test_list_orgs(self, auth_client, user, org_with_owner):
        response = auth_client.get('/api/v1/organizations/')
        assert response.status_code == 200
        assert response.data['success'] == True

    def test_get_org_detail(self, auth_client, org_with_owner):
        response = auth_client.get(f'/api/v1/organizations/{org_with_owner.slug}/')
        assert response.status_code == 200

    def test_get_org_not_member(self, auth_client):
        other_org = OrganizationFactory()
        response = auth_client.get(f'/api/v1/organizations/{other_org.slug}/')
        assert response.status_code == 403

    def test_update_org(self, auth_client, org_with_owner):
        response = auth_client.patch(f'/api/v1/organizations/{org_with_owner.slug}/', {
            'name': 'Updated Name',
        }, format='json')
        assert response.status_code == 200

    def test_delete_org(self, auth_client, org_with_owner):
        response = auth_client.delete(f'/api/v1/organizations/{org_with_owner.slug}/')
        assert response.status_code == 200
