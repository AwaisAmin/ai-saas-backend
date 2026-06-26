import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from tests.factories import UserFactory
from apps.core.users.models import SocialAccount

@pytest.fixture
def client():
    return APIClient()

def make_google_mock(social_id="google_123", email="googleuser@example.com", name="John Doe"):
    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "fake_google_token"}

    userinfo_response = MagicMock()
    userinfo_response.json.return_value = {
        "id": social_id,
        "email": email,
        "name": name,
    }
    return [token_response, userinfo_response]

def make_github_mock(social_id="github_456", email="githubuser@example.com", name="Jane Doe"):
    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "fake_github_token"}

    userinfo_response = MagicMock()
    userinfo_response.json.return_value = {
        "id": social_id,
        "email": email,
        "name": name,
        "login": "janedoe",
    }
    return [token_response, userinfo_response]

@pytest.mark.django_db
class TestGoogleOAuth:
    def test_google_login_new_user(self, client):
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_google_mock()[0]
            mock_get.return_value = make_google_mock()[1]

            response = client.post("/api/v1/auth/social/google/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        assert response.status_code == 200
        assert response.data["data"]["tokens"]["access_token"] is not None
        assert response.data["data"]["user"]["email"] == "googleuser@example.com"
        assert response.data["data"]["user"]["is_verified"] is True

    def test_google_login_creates_social_account(self, client):
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_google_mock()[0]
            mock_get.return_value = make_google_mock()[1]

            client.post("/api/v1/auth/social/google/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        assert SocialAccount.objects.filter(provider="google", social_id="google_123").exists()

    def test_google_login_existing_user_links_account(self, client):
        existing_user = UserFactory(email="googleuser@example.com")

        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_google_mock()[0]
            mock_get.return_value = make_google_mock()[1]

            response = client.post("/api/v1/auth/social/google/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        assert response.status_code == 200
        assert response.data["data"]["user"]["id"] == str(existing_user.id)
        assert SocialAccount.objects.filter(user=existing_user, provider="google").exists()

    def test_google_login_second_time_uses_existing_social_account(self, client):
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_google_mock()[0]
            mock_get.return_value = make_google_mock()[1]
            client.post("/api/v1/auth/social/google/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_google_mock()[0]
            mock_get.return_value = make_google_mock()[1]
            response = client.post("/api/v1/auth/social/google/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        assert response.status_code == 200
        assert SocialAccount.objects.filter(provider="google", social_id="google_123").count() == 1

    def test_google_invalid_code(self, client):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.json.return_value = {"error": "invalid_grant"}

            response = client.post("/api/v1/auth/social/google/", {
                "code": "bad_code",
                "redirect_uri": "http://localhost:3000/callback/google",
            }, format="json")

        assert response.status_code == 401

    def test_google_missing_code(self, client):
        response = client.post("/api/v1/auth/social/google/", {
            "redirect_uri": "http://localhost:3000/callback/google",
        }, format="json")
        assert response.status_code == 400

    def test_unsupported_provider(self, client):
        response = client.post("/api/v1/auth/social/facebook/", {
            "code": "fake_code",
        }, format="json")
        assert response.status_code == 400

@pytest.mark.django_db
class TestGitHubOAuth:
    def test_github_login_new_user(self, client):
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_github_mock()[0]
            mock_get.return_value = make_github_mock()[1]

            response = client.post("/api/v1/auth/social/github/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/github",
            }, format="json")

        assert response.status_code == 200
        assert response.data["data"]["user"]["email"] == "githubuser@example.com"
        assert response.data["data"]["user"]["is_verified"] is True

    def test_github_login_creates_social_account(self, client):
        with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
            mock_post.return_value = make_github_mock()[0]
            mock_get.return_value = make_github_mock()[1]

            client.post("/api/v1/auth/social/github/", {
                "code": "fake_code",
                "redirect_uri": "http://localhost:3000/callback/github",
            }, format="json")

        assert SocialAccount.objects.filter(provider="github", social_id="github_456").exists()

    def test_github_invalid_code(self, client):
        with patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock()
            mock_post.return_value.json.return_value = {"error": "bad_verification_code"}

            response = client.post("/api/v1/auth/social/github/", {
                "code": "bad_code",
                "redirect_uri": "http://localhost:3000/callback/github",
            }, format="json")

        assert response.status_code == 401
