import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory, ProjectFactory, TaskFactory
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
def project(db, org):
    return ProjectFactory(organization=org)

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
class TestTasks:
    def test_create_task_success(self, auth_client, org, project):
        response = auth_client.post(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/',
            {
                'title': 'Test Task',
                'status': 'todo',
                'priority': 'medium',
            },
            format='json',
        )
        assert response.status_code == 201
        assert response.data['data']['title'] == 'Test Task'

    def test_create_task_unauthenticated(self, org, project):
        client = APIClient()
        response = client.post(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/',
            {'title': 'Test Task'},
            format='json',
        )
        assert response.status_code == 401

    def test_list_tasks(self, auth_client, org, project):
        TaskFactory(project=project)
        TaskFactory(project=project)
        response = auth_client.get(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/'
        )
        assert response.status_code == 200
        assert len(response.data['results']) >= 2

    def test_get_task_detail(self, auth_client, org, project):
        task = TaskFactory(project=project)
        response = auth_client.get(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/{task.id}/'
        )
        assert response.status_code == 200
        assert response.data['data']['title'] == task.title

    def test_update_task_status(self, auth_client, org, project):
        task = TaskFactory(project=project)
        response = auth_client.patch(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/{task.id}/',
            {'status': 'in_progress'},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['data']['status'] == 'in_progress'

    def test_delete_task(self, auth_client, org, project):
        task = TaskFactory(project=project)
        response = auth_client.delete(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/{task.id}/'
        )
        assert response.status_code == 200
    
    def test_viewer_cannot_create_task(self, user, org, project):
        MembershipFactory(user=user, organization=org, role=Membership.RoleChoices.VIEWER)
        client = APIClient()
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.post(
            f'/api/v1/organizations/{org.slug}/projects/{project.id}/tasks/',
            {'title': 'Test Task'},
            format='json',
        )
        assert response.status_code == 403

