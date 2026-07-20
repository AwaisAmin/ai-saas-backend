import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory, ProjectFactory
from apps.core.organizations.models import Membership
from apps.billing.subscriptions.models import Subscription
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
    token = response.data['data']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestSubscriptionLimits:
    def test_free_plan_project_limit(self, auth_client, org):
        ProjectFactory(organization=org)
        ProjectFactory(organization=org)
        ProjectFactory(organization=org)
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/projects/', {
            'name': '4th Project',
        }, format='json')
        assert response.status_code == 403
        assert 'plan' in response.data['message'].lower()

    def test_free_plan_member_limit(self, auth_client, org):
        for _ in range(4):
            u = UserFactory()
            MembershipFactory(user=u, organization=org, role=Membership.RoleChoices.MEMBER)
        new_user = UserFactory()
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/', {
            'email': new_user.email,
            'role': 'member',
        }, format='json')
        assert response.status_code == 403
        assert 'plan' in response.data['message'].lower()

    def test_pro_plan_no_project_limit(self, auth_client, org):
        sub, _ = Subscription.objects.get_or_create(
            organization=org,
            defaults={'plan': 'free'}
        )
        sub.plan = 'pro'
        sub.save()

        for i in range(5):
            ProjectFactory(organization=org)

        response = auth_client.post(f'/api/v1/organizations/{org.slug}/projects/', {
            'name': 'Extra Project',
        }, format='json')
        assert response.status_code == 201

    def test_free_plan_ai_limit(self, auth_client, org):
        from unittest.mock import patch, AsyncMock

        for _ in range(10):
            ActivityLog.objects.create(
                organization=org,
                action=ActivityLog.ActionChoices.AI_CALL,
                entity_type=ActivityLog.EntityTypeChoices.AI,
            )

        with patch('apps.intelligence.views.generate', new=AsyncMock(return_value={'data': {}})):
            response = auth_client.post('/api/v1/ai/generate-tasks/', {
                'org_slug': org.slug,
                'prompt': 'test',
            }, format='json')
        assert response.status_code == 403
