"""Tests for HTTP Basic Authentication."""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from fitness.app import app
from fitness.app.dependencies import strava_client


@pytest.fixture(scope="function")
def override_strava_client():
    """Effectively disable the Strava client for the duration of the test, to avoid it trying to refresh the token."""
    app.dependency_overrides[strava_client] = lambda: None
    yield
    app.dependency_overrides = {}


class TestAuthenticationEndpoints:
    """Test HTTP Basic Authentication on endpoints."""

    def test_update_data_requires_auth(self, client: TestClient):
        """POST /update-data should require authentication."""
        response = client.post("/strava/update-data")
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Basic"

    def test_update_data_with_valid_credentials(
        self, auth_client: TestClient, monkeypatch, override_strava_client
    ):
        """POST /strava/update-data should succeed with valid credentials."""
        with monkeypatch.context() as m:
            m.setattr("fitness.app.routers.strava.load_strava_runs", lambda client: [])
            m.setattr("fitness.app.routers.strava.get_existing_run_ids", lambda: [])
            response = auth_client.post("/strava/update-data")

        assert response.status_code == 200
        data = response.json()
        assert data["inserted_count"] == 0

    def test_update_data_with_invalid_username(self, client: TestClient):
        """POST /strava/update-data should fail with invalid username."""
        response = client.post("/strava/update-data", auth=("wronguser", "testpass"))
        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication credentials" in data["detail"]

    def test_update_data_with_invalid_password(self, client: TestClient):
        """POST /strava/update-data should fail with invalid password."""
        response = client.post("/strava/update-data", auth=("testuser", "wrongpass"))
        assert response.status_code == 401

    def test_read_runs_no_auth_required(self, client: TestClient):
        """GET /runs should not require authentication."""
        with patch("fitness.app.dependencies.all_runs") as mock_runs:
            mock_runs.return_value = []
            response = client.get("/runs")
            assert response.status_code == 200

    def test_health_endpoint_no_auth(self, client: TestClient):
        """GET /health should remain public."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_auth_verify_requires_auth(self, client: TestClient):
        """GET /auth/verify should require authentication."""
        response = client.get("/auth/verify")
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers

    def test_auth_verify_with_valid_credentials(self, auth_client: TestClient):
        """GET /auth/verify should succeed with valid credentials."""
        response = auth_client.get("/auth/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"
        assert data["username"] == os.environ["BASIC_AUTH_USERNAME"]

    def test_auth_verify_with_invalid_credentials(self, client: TestClient):
        """GET /auth/verify should fail with invalid credentials."""
        response = client.get("/auth/verify", auth=("wronguser", "wrongpass"))
        assert response.status_code == 401

    def test_metrics_no_auth_required(self, client: TestClient):
        """GET /metrics/* endpoints should not require authentication."""
        with patch("fitness.app.dependencies.all_runs") as mock_runs:
            mock_runs.return_value = []
            response = client.get("/metrics/mileage/total")
            assert response.status_code == 200


class TestProtectedMutationEndpoints:
    """Test that all mutation endpoints are properly protected."""

    @pytest.mark.parametrize(
        "method,path",
        [
            ("POST", "/strava/update-data"),
            ("PATCH", "/runs/test_run_123"),
            ("POST", "/runs/test_run_123/restore/1"),
            ("PATCH", "/shoes/test_shoe_id"),
            ("POST", "/sync/runs/test_run_123"),
            ("DELETE", "/sync/runs/test_run_123"),
        ],
    )
    def test_mutation_endpoints_require_auth(self, method, path, client: TestClient):
        """All mutation endpoints should return 401 without auth."""
        # Prepare request body for endpoints that need it
        body = {}
        if "runs" in path and method == "PATCH":
            body = {"changed_by": "test", "distance": 5.0}
        elif "shoes" in path:
            body = {"retired_at": "2024-01-01"}

        kwargs = {"json": body} if body else {}
        response = client.request(method, path, **kwargs)
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers

    @pytest.mark.parametrize(
        "path",
        [
            "/runs",
            "/runs/details",
            "/runs-details",
            "/metrics/mileage/total",
            "/metrics/mileage/by-shoe",
            "/metrics/seconds/total",
            "/shoes",
            "/health",
            "/environment",
        ],
    )
    def test_read_endpoints_no_auth(self, path, client: TestClient):
        """Read endpoints should work without authentication."""
        with patch("fitness.app.dependencies.all_runs") as mock_runs:
            mock_runs.return_value = []
            with patch("fitness.db.shoes.get_shoes") as mock_shoes:
                mock_shoes.return_value = []
                response = client.get(path)
                # Should not be 401 (may be 200 or other valid response code)
                assert response.status_code != 401


class TestAuthModule:
    """Test the auth module functions directly."""

    def test_get_auth_credentials_success(self, monkeypatch, client: TestClient):
        """get_auth_credentials should load from environment."""
        from fitness.app.auth import get_auth_credentials

        monkeypatch.setenv("BASIC_AUTH_USERNAME", "admin")
        monkeypatch.setenv("BASIC_AUTH_PASSWORD", "secret123")

        username, password = get_auth_credentials()
        assert username == "admin"
        assert password == "secret123"

    def test_get_auth_credentials_missing(self, monkeypatch):
        """get_auth_credentials should raise if not configured."""
        from fitness.app.auth import get_auth_credentials

        monkeypatch.delenv("BASIC_AUTH_USERNAME", raising=False)
        monkeypatch.delenv("BASIC_AUTH_PASSWORD", raising=False)

        with pytest.raises(ValueError) as exc_info:
            get_auth_credentials()
        assert "BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD must be set" in str(
            exc_info.value
        )
