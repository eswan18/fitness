"""Basic tests for OAuth router endpoints."""

import os
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from fitness.db.oauth_credentials import OAuthCredentials, OAuthIntegrationStatus


class TestStravaAuthStatus:
    """Test GET /oauth/strava/status endpoint."""

    def test_status_no_credentials(self, client: TestClient):
        """Test status endpoint when no credentials exist."""
        with patch("fitness.app.routers.oauth.get_credentials", return_value=None):
            response = client.get("/oauth/strava/status")

        assert response.status_code == 200
        data = response.json()
        assert data["authorized"] is False
        assert data["access_token_valid"] is None
        assert data["expires_at"] is None

    def test_status_with_valid_credentials(self, client: TestClient):
        """Test status endpoint when valid credentials exist."""
        future_expiry = datetime.now(timezone.utc).replace(year=2025, month=12, day=31)
        creds = OAuthCredentials(
            provider="strava",
            client_id="test_client_id",
            client_secret="test_secret",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=future_expiry,
        )

        with patch("fitness.app.routers.oauth.get_credentials", return_value=creds):
            response = client.get("/oauth/strava/status")

        assert response.status_code == 200
        data = response.json()
        assert data["authorized"] is True
        assert data["access_token_valid"] is True
        assert data["expires_at"] is not None

    def test_status_with_expired_credentials(self, client: TestClient):
        """Test status endpoint when credentials are expired."""
        past_expiry = datetime.now(timezone.utc).replace(year=2020, month=1, day=1)
        creds = OAuthCredentials(
            provider="strava",
            client_id="test_client_id",
            client_secret="test_secret",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=past_expiry,
        )

        with patch("fitness.app.routers.oauth.get_credentials", return_value=creds):
            response = client.get("/oauth/strava/status")

        assert response.status_code == 200
        data = response.json()
        assert data["authorized"] is True
        assert data["access_token_valid"] is False


class TestStravaAuthorize:
    """Test GET /oauth/strava/authorize endpoint."""

    def test_authorize_redirects(self, client: TestClient):
        """Test that authorize endpoint redirects to Strava OAuth URL."""
        with patch(
            "fitness.app.routers.oauth.strava.build_oauth_authorize_url"
        ) as mock_build:
            mock_build.return_value = (
                "https://www.strava.com/oauth/authorize?client_id=123"
            )
            with patch(
                "fitness.app.routers.oauth.PUBLIC_API_BASE_URL",
                "https://api.example.com",
            ):
                response = client.get("/oauth/strava/authorize", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert (
            response.headers["location"]
            == "https://www.strava.com/oauth/authorize?client_id=123"
        )
        mock_build.assert_called_once_with(
            redirect_uri="https://api.example.com/oauth/strava/callback"
        )


class TestStravaCallback:
    """Test GET /oauth/strava/callback endpoint."""

    def test_callback_missing_code(self, client: TestClient):
        """Test callback endpoint when code is missing."""
        response = client.get("/oauth/strava/callback")

        assert response.status_code == 400
        assert "No code provided" in response.json()["detail"]

    @patch("fitness.app.routers.oauth.upsert_credentials")
    def test_callback_success(self, mock_upsert, client: TestClient):
        """Test successful OAuth callback."""
        # Mock the token exchange
        future_date = datetime.now(timezone.utc).replace(year=2025, month=12, day=31)
        mock_token = type(
            "Token",
            (),
            {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_at_datetime": lambda self=None: future_date,
            },
        )()

        with patch(
            "fitness.app.routers.oauth.strava.exchange_code_for_token",
            new_callable=AsyncMock,
        ) as mock_exchange:
            mock_exchange.return_value = mock_token
            with patch("fitness.app.routers.oauth.strava.CLIENT_ID", "test_client_id"):
                with patch(
                    "fitness.app.routers.oauth.strava.CLIENT_SECRET", "test_secret"
                ):
                    with patch(
                        "fitness.app.routers.oauth.PUBLIC_DASHBOARD_BASE_URL",
                        "https://dashboard.example.com",
                    ):
                        response = client.get(
                            "/oauth/strava/callback?code=test_code",
                            follow_redirects=False,
                        )

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "https://dashboard.example.com"

        # Verify token exchange was called
        mock_exchange.assert_called_once_with("test_code")

        # Verify credentials were saved
        mock_upsert.assert_called_once()
        saved_creds = mock_upsert.call_args[0][0]
        assert isinstance(saved_creds, OAuthCredentials)
        assert saved_creds.provider == "strava"
        assert saved_creds.access_token == "new_access_token"
        assert saved_creds.refresh_token == "new_refresh_token"
        assert saved_creds.client_id == "test_client_id"
        assert saved_creds.client_secret == "test_secret"
