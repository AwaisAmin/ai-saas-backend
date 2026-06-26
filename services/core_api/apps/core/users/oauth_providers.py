import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
import requests

class OAuthError(Exception):
    pass

@dataclass
class OAuthUserInfo:
    social_id: str
    email: str
    first_name: str
    last_name: str
    provider: str

class BaseOAuthProvider(ABC):
    @abstractmethod
    def exchange_code(self, code: str, redirect_uri: str) -> str:
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        pass

    def authenticate(self, code: str, redirect_uri: str) -> OAuthUserInfo:
        try:
            access_token = self.exchange_code(code, redirect_uri)
            return self.get_user_info(access_token)
        except OAuthError:
            raise
        except Exception as e:
            raise OAuthError(f"Authentication failed: {str(e)}")

class GoogleOAuthProvider(BaseOAuthProvider):
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def exchange_code(self, code: str, redirect_uri: str) -> str:
        response = requests.post(self.TOKEN_URL, data={
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        data = response.json()
        if "access_token" not in data:
            raise OAuthError("Failed to exchange Google authorization code")
        return data["access_token"]

    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        response = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        data = response.json()
        if "id" not in data:
            raise OAuthError("Failed to fetch Google user info")

        name_parts = data.get("name", "").split(" ", 1)
        return OAuthUserInfo(
            social_id=str(data["id"]),
            email=data.get("email", ""),
            first_name=name_parts[0] if name_parts else "",
            last_name=name_parts[1] if len(name_parts) > 1 else "",
            provider="google",
        )

class GitHubOAuthProvider(BaseOAuthProvider):
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    USER_EMAIL_URL = "https://api.github.com/user/emails"

    def exchange_code(self, code: str, redirect_uri: str) -> str:
        response = requests.post(self.TOKEN_URL, data={
            "code": code,
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
        }, headers={"Accept": "application/json"})
        data = response.json()
        if "access_token" not in data:
            raise OAuthError("Failed to exchange GitHub authorization code")
        return data["access_token"]

    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(self.USER_INFO_URL, headers=headers)
        data = response.json()
        if "id" not in data:
            raise OAuthError("Failed to fetch GitHub user info")

        email = data.get("email")
        if not email:
            email_response = requests.get(self.USER_EMAIL_URL, headers=headers)
            emails = email_response.json()
            primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
            if not primary:
                raise OAuthError("No verified email found on GitHub account")
            email = primary["email"]

        name_parts = (data.get("name") or "").split(" ", 1)
        return OAuthUserInfo(
            social_id=str(data["id"]),
            email=email,
            first_name=name_parts[0] if name_parts else data.get("login", ""),
            last_name=name_parts[1] if len(name_parts) > 1 else "",
            provider="github",
        )
