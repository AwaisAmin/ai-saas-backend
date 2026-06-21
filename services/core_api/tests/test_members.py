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
    token = response.data['data']['tokens']['access_token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
class TestMembers:
    def test_list_members(self, auth_client, org):
        response = auth_client.get(f'/api/v1/organizations/{org.slug}/members/')
        assert response.status_code == 200
        assert len(response.data['data']) >= 1

    def test_invite_member(self, auth_client, org):
        new_user = UserFactory()
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/', {
            'email': new_user.email,
            'role': 'member',
        }, format='json')
        assert response.status_code == 201

    def test_invite_member_unauthenticated(self, org):
        client = APIClient()
        new_user = UserFactory()
        response = client.post(f'/api/v1/organizations/{org.slug}/members/', {
            'email': new_user.email,
            'role': 'member',
        }, format='json')
        assert response.status_code == 401

    def test_invite_nonexistent_user(self, auth_client, org):
        response = auth_client.post(f'/api/v1/organizations/{org.slug}/members/', {
            'email': 'notexist@test.com',
            'role': 'member',
        }, format='json')
        assert response.status_code == 400

    def test_viewer_cannot_invite(self, user, org):
        MembershipFactory(user=user, organization=org, role=Membership.RoleChoices.VIEWER)
        client = APIClient()
        response = client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'TestPass123!',
        }, format='json')
        token = response.data['data']['tokens']['access_token']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        new_user = UserFactory()
        response = client.post(f'/api/v1/organizations/{org.slug}/members/', {
            'email': new_user.email,
            'role': 'member',
        }, format='json')
        assert response.status_code == 403

    def test_update_member_role(self, auth_client, org):
        new_user = UserFactory()
        m = MembershipFactory(user=new_user, organization=org, role=Membership.RoleChoices.MEMBER)
        response = auth_client.patch(f'/api/v1/organizations/{org.slug}/members/{m.id}/', {
            'role': 'admin',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['role'] == 'admin'

    def test_remove_member(self, auth_client, org):
        new_user = UserFactory()
        m = MembershipFactory(user=new_user, organization=org, role=Membership.RoleChoices.MEMBER)
        response = auth_client.delete(f'/api/v1/organizations/{org.slug}/members/{m.id}/')
        assert response.status_code == 200
