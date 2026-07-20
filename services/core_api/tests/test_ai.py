import pytest
from unittest.mock import patch, AsyncMock
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory
from apps.core.organizations.models import Membership

MOCK_RESULT = {'data': {'text': 'mocked AI response'}}

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
class TestAI:
    def test_generate_success(self, auth_client, org):
        with patch('apps.intelligence.views.generate', new=AsyncMock(return_value=MOCK_RESULT)):
            response = auth_client.post('/api/v1/ai/generate-tasks/', {
                'org_slug': org.slug,
                'prompt': 'Write a test description',
            }, format='json')
        assert response.status_code == 200

    def test_generate_missing_fields(self, auth_client, org):
        response = auth_client.post('/api/v1/ai/generate-tasks/', {
            'org_slug': org.slug,
        }, format='json')
        assert response.status_code == 400

    def test_summarize_success(self, auth_client, org):
        with patch('apps.intelligence.views.summarize', new=AsyncMock(return_value=MOCK_RESULT)):
            response = auth_client.post('/api/v1/ai/summarize-project/', {
                'org_slug': org.slug,
                'content': 'This is content to summarize',
            }, format='json')
        assert response.status_code == 200

    def test_suggest_success(self, auth_client, org):
        with patch('apps.intelligence.views.suggest', new=AsyncMock(return_value=MOCK_RESULT)):
            response = auth_client.post('/api/v1/ai/suggest-assignee/', {
                'org_slug': org.slug,
                'task_title': 'Fix login bug',
                'context': 'Users cannot login with correct credentials',
            }, format='json')
        assert response.status_code == 200

    def test_ai_unauthenticated(self, org):
        client = APIClient()
        response = client.post('/api/v1/ai/generate-tasks/', {
            'org_slug': org.slug,
            'prompt': 'test',
        }, format='json')
        assert response.status_code == 401

    def test_ai_non_member(self, org):
        other_user = UserFactory()
        client = APIClient()
        response = client.post('/api/v1/auth/login/', {
            'email': other_user.email,
            'password': 'TestPass123!',
        }, format='json')
        token = response.data['data']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        with patch('apps.intelligence.views.generate', new=AsyncMock(return_value=MOCK_RESULT)):
            response = client.post('/api/v1/ai/generate-tasks/', {
                'org_slug': org.slug,
                'prompt': 'test',
            }, format='json')
        assert response.status_code == 403
