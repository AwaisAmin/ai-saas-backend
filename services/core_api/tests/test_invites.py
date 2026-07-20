import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory, PendingInviteFactory
from apps.core.organizations.models import Membership, PendingInvite

@pytest.fixture
def owner(db):
    return UserFactory()

@pytest.fixture
def org(db):
    return OrganizationFactory()

@pytest.fixture
def membership(db, owner, org):
    return MembershipFactory(user=owner, organization=org, role=Membership.RoleChoices.OWNER)

@pytest.fixture
def auth_client(owner, membership):
    client = APIClient()
    response = client.post('/api/v1/auth/login/', {
        'email': owner.email,
        'password': 'TestPass123!',
    }, format='json')
    token = response.data['data']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestBulkInvite:
    def test_bulk_invite_success(self, auth_client, org):
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/bulk-invite/', {
            'invites': [
                {'email': 'a@test.com', 'role': 'member'},
                {'email': 'b@test.com', 'role': 'admin'},
            ]
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['sent'] == 2
        assert response.data['data']['skipped'] == 0

    def test_bulk_invite_skips_existing_members(self, auth_client, org, owner):
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/bulk-invite/', {
            'invites': [
                {'email': owner.email, 'role': 'member'},
            ]
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['skipped'] == 1

    def test_bulk_invite_advances_onboarding(self, auth_client, org, owner):
        owner.onboarding_step = owner.OnboardingStep.ORG_CREATED
        owner.save()
        auth_client.post(f'/api/v1/organizations/{org.slug}/members/bulk-invite/', {
            'invites': [{'email': 'x@test.com', 'role': 'member'}]
        }, format='json')
        owner.refresh_from_db()
        assert owner.onboarding_step == owner.OnboardingStep.TEAM_INVITED

    def test_bulk_invite_unauthenticated(self, org):
        client = APIClient()
        response = client.post(f'/api/v1/organizations/{org.slug}/members/bulk-invite/', {
            'invites': [{'email': 'x@test.com', 'role': 'member'}]
        }, format='json')
        assert response.status_code == 401

    def test_bulk_invite_empty_list(self, auth_client, org):
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/bulk-invite/', {
            'invites': []
        }, format='json')
        assert response.status_code == 400

@pytest.mark.django_db
class TestInvitePreview:
    def test_preview_valid_token(self, auth_client, org):
        invite = PendingInviteFactory(organization=org)
        response = auth_client.get(f'/api/v1/organizations/invite/preview/?token={invite.token}')
        assert response.status_code == 200
        assert response.data['data']['email'] == invite.email
        assert response.data['data']['already_accepted'] is False

    def test_preview_already_accepted(self, auth_client, org):
        invite = PendingInviteFactory(organization=org, is_accepted=True)
        response = auth_client.get(f'/api/v1/organizations/invite/preview/?token={invite.token}')
        assert response.status_code == 200
        assert response.data['data']['already_accepted'] is True

    def test_preview_expired_token(self, auth_client, org):
        invite = PendingInviteFactory(
            organization=org,
            expires_at=timezone.now() - timedelta(days=1),
        )
        response = auth_client.get(f'/api/v1/organizations/invite/preview/?token={invite.token}')
        assert response.status_code == 404

    def test_preview_invalid_token(self, auth_client):
        response = auth_client.get('/api/v1/organizations/invite/preview/?token=00000000-0000-0000-0000-000000000000')
        assert response.status_code == 404

    def test_preview_unauthenticated(self, org):
        invite = PendingInviteFactory(organization=org)
        client = APIClient()
        response = client.get(f'/api/v1/organizations/invite/preview/?token={invite.token}')
        assert response.status_code == 401

@pytest.mark.django_db
class TestInviteRespond:
    def test_accept_invite(self, org, db):
        invited_user = UserFactory()
        invite = PendingInviteFactory(organization=org, email=invited_user.email)
        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': invited_user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.post('/api/v1/organizations/invite/respond/', {
            'token': str(invite.token),
            'action': 'accept',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['org_slug'] == org.slug
        assert Membership.objects.filter(user=invited_user, organization=org).exists()

    def test_decline_invite(self, org, db):
        invited_user = UserFactory()
        invite = PendingInviteFactory(organization=org, email=invited_user.email)
        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': invited_user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.post('/api/v1/organizations/invite/respond/', {
            'token': str(invite.token),
            'action': 'decline',
        }, format='json')
        assert response.status_code == 200
        assert not PendingInvite.objects.filter(id=invite.id).exists()

    def test_wrong_user_cannot_accept(self, org, db):
        invited_user = UserFactory()
        wrong_user = UserFactory()
        invite = PendingInviteFactory(organization=org, email=invited_user.email)
        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': wrong_user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.post('/api/v1/organizations/invite/respond/', {
            'token': str(invite.token),
            'action': 'accept',
        }, format='json')
        assert response.status_code == 400

    def test_invalid_action(self, org, db):
        invited_user = UserFactory()
        invite = PendingInviteFactory(organization=org, email=invited_user.email)
        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': invited_user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.post('/api/v1/organizations/invite/respond/', {
            'token': str(invite.token),
            'action': 'maybe',
        }, format='json')
        assert response.status_code == 400

@pytest.mark.django_db
class TestMyPendingInvites:
    def test_returns_pending_invites_for_user(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        PendingInviteFactory(organization=org, email=user.email)

        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.get('/api/v1/organizations/my-invites/')
        assert response.status_code == 200
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['org_name'] == org.name

    def test_does_not_return_other_users_invites(self, db):
        user = UserFactory()
        other_user = UserFactory()
        org = OrganizationFactory()
        PendingInviteFactory(organization=org, email=other_user.email)

        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.get('/api/v1/organizations/my-invites/')
        assert response.status_code == 200
        assert len(response.data['data']) == 0

    def test_does_not_return_accepted_invites(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        PendingInviteFactory(organization=org, email=user.email, is_accepted=True)

        client = APIClient()
        login = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["data"]["access_token"]}')

        response = client.get('/api/v1/organizations/my-invites/')
        assert response.status_code == 200
        assert len(response.data['data']) == 0

    def test_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/v1/organizations/my-invites/')
        assert response.status_code == 401
