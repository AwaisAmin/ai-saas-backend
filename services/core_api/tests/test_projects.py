import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory, ProjectFactory
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
class TestProjects:
    def test_create_project_success(self, auth_client, org):
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/projects/', {
            'name': 'Test Project',
            'description': 'A test project',
        }, format='json')
        assert response.status_code == 201
        assert response.data['data']['name'] == 'Test Project'

    def test_create_project_unauthenticated(self, org):
        client = APIClient()
        response = client.post(f'/api/v1/organizations/{org.slug}/projects/', {
            'name': 'Test Project',
        }, format='json')
        assert response.status_code == 401

    def test_list_projects(self, auth_client, org):
        ProjectFactory(organization=org)
        ProjectFactory(organization=org)
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/projects/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 2

    def test_get_project_detail(self, auth_client, org):
        project = ProjectFactory(organization=org)
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/projects/{project.id}/')
        assert response.status_code == 200
        assert response.data['data']['name'] == project.name

    def test_update_project(self, auth_client, org):
        project = ProjectFactory(organization=org)
        response = auth_client.patch(f'/api/v1/organizations/{org.slug}/projects/{project.id}/', {
            'name': 'Updated Name',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['name'] == 'Updated Name'

    def test_delete_project(self, auth_client, org):
        project = ProjectFactory(organization=org)
        response = auth_client.delete(f'/api/v1/organizations/{org.slug}/projects/{project.id}/')
        assert response.status_code == 200

    def test_viewer_cannot_create_project(self, user, org):
        MembershipFactory(user=user, organization=org, role=Membership.RoleChoices.VIEWER)
        client = APIClient()
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.post(f'/api/v1/organizations/{org.slug}/projects/', {
            'name': 'Test Project',
        }, format='json')
        assert response.status_code == 403
