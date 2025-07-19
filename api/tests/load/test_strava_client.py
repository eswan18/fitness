from unittest.mock import MagicMock
import datetime

import dotenv
import pytest
import httpx

from fitness.load.strava import StravaClient, StravaCreds, StravaActivity, StravaGear
from fitness.load.strava.models import StravaToken


@pytest.fixture(scope="session")
def real_strava_client():
    dotenv.load_dotenv()
    return StravaClient.from_env()


def test_init_from_env(monkeypatch):
    """Test that the StravaClient can be initialized from environment variables."""
    # We need to stub this method to avoid making a real HTTP request, which will fail due to the fake creds.
    with monkeypatch.context() as m:
        m.setenv("STRAVA_CLIENT_ID", "test_client_id")
        m.setenv("STRAVA_CLIENT_SECRET", "test_client_secret")
        m.setenv("STRAVA_REFRESH_TOKEN", "test_refresh_token")
        fake_get_auth_token = MagicMock(return_value="test_auth_token")
        m.setattr(StravaClient, "_get_auth_token", fake_get_auth_token)
        client = StravaClient.from_env()
    # Make sure these creds are the ones stored on the client.
    assert client.creds.client_id == "test_client_id"
    assert client.creds.client_secret == "test_client_secret"
    assert client.creds.refresh_token == "test_refresh_token"
    # Make sure these creds got passed to the stubbed method.
    fake_get_auth_token.assert_called_once_with(client.creds)


def test_init_from_env_missing_env_vars(monkeypatch):
    """Test that the StravaClient raises an error if env vars are missing."""
    with monkeypatch.context() as m:
        m.delenv("STRAVA_CLIENT_ID", raising=False)
        m.delenv("STRAVA_CLIENT_SECRET", raising=False)
        m.delenv("STRAVA_REFRESH_TOKEN", raising=False)
        with pytest.raises(ValueError):
            StravaClient.from_env()


def test_init_from_env_no_env_vars(monkeypatch):
    """Test that the StravaClient can be initialized via direct arguments."""
    with monkeypatch.context() as m:
        fake_get_auth_token = MagicMock(return_value="test_auth_token")
        m.setattr(StravaClient, "_get_auth_token", fake_get_auth_token)
        client = StravaClient(
            creds=StravaCreds(
                client_id="test_client_id",
                client_secret="test_client_secret",
                refresh_token="test_refresh_token",
            )
        )
    assert client.creds.client_id == "test_client_id"
    assert client.creds.client_secret == "test_client_secret"
    assert client.creds.refresh_token == "test_refresh_token"
    # Make sure these creds got passed to the stubbed method.
    fake_get_auth_token.assert_called_once_with(client.creds)


@pytest.mark.integration("strava")
def test_get_activities(real_strava_client: StravaClient):
    activities = real_strava_client.get_activities()
    assert len(activities) > 0
    assert all(isinstance(activity, StravaActivity) for activity in activities)


@pytest.mark.integration("strava")
def test_get_gear(real_strava_client: StravaClient):
    # This is cheating, but I know these two Gear IDs exist in my Strava account
    ids = ["g18184182", "g20299197"]
    gear = real_strava_client.get_gear(ids)
    assert len(gear) == len(ids)
    assert all(isinstance(g, StravaGear) for g in gear)


def test_refresh_access_token_success(monkeypatch):
    """Test successful token refresh."""
    creds = StravaCreds(
        client_id="test_client_id",
        client_secret="test_client_secret", 
        refresh_token="test_refresh_token"
    )
    
    # Create an expired token
    expired_token = StravaToken(
        token_type="Bearer",
        access_token="old_access_token",
        expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) - 3600,  # 1 hour ago
        expires_in=3600,
        refresh_token="test_refresh_token"
    )
    
    # Create a new token that would be returned from refresh
    new_token = StravaToken(
        token_type="Bearer", 
        access_token="new_access_token",
        expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600,  # 1 hour from now
        expires_in=3600,
        refresh_token="new_refresh_token"
    )
    
    with monkeypatch.context() as m:
        # Mock the HTTP request
        mock_response = MagicMock()
        mock_response.content = new_token.model_dump_json().encode()
        mock_response.raise_for_status.return_value = None
        m.setattr(httpx, "post", MagicMock(return_value=mock_response))
        
        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token", 
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600,
            expires_in=3600,
            refresh_token="fake_refresh"
        )
        m.setattr(StravaClient, "_get_auth_token", MagicMock(return_value=fake_token))
        
        client = StravaClient(creds=creds, auto_reconnect=False)
        client._auth_token = expired_token
        
        # Test the refresh
        result = client._refresh_access_token()
        
        assert result is True
        assert client._auth_token.access_token == "new_access_token"
        assert client.creds.refresh_token == "new_refresh_token"  # Should update stored refresh token


def test_refresh_access_token_failure(monkeypatch):
    """Test failed token refresh."""
    creds = StravaCreds(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token"
    )
    
    with monkeypatch.context() as m:
        # Mock a failed HTTP request
        m.setattr(httpx, "post", MagicMock(side_effect=httpx.HTTPStatusError("", request=MagicMock(), response=MagicMock())))
        
        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token", 
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600,
            expires_in=3600,
            refresh_token="fake_refresh"
        )
        m.setattr(StravaClient, "_get_auth_token", MagicMock(return_value=fake_token))
        
        client = StravaClient(creds=creds, auto_reconnect=False)
        
        # Test the refresh failure
        result = client._refresh_access_token()
        
        assert result is False


def test_pre_request_check_tries_refresh_before_full_oauth(monkeypatch):
    """Test that _pre_request_check tries token refresh before falling back to full OAuth."""
    creds = StravaCreds(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token"
    )
    
    with monkeypatch.context() as m:
        mock_refresh = MagicMock(return_value=True)
        mock_connect = MagicMock()
        mock_has_valid_token = MagicMock(return_value=False)
        
        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token", 
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600,
            expires_in=3600,
            refresh_token="fake_refresh"
        )
        m.setattr(StravaClient, "_get_auth_token", MagicMock(return_value=fake_token))
        
        client = StravaClient(creds=creds, auto_reconnect=True)
        m.setattr(client, "_refresh_access_token", mock_refresh)
        m.setattr(client, "connect", mock_connect)
        m.setattr(client, "has_valid_token", mock_has_valid_token)
        
        client._pre_request_check()
        
        # Should try refresh first
        mock_refresh.assert_called_once()
        # Should not call connect since refresh succeeded
        mock_connect.assert_not_called()


def test_pre_request_check_falls_back_to_oauth_if_refresh_fails(monkeypatch):
    """Test that _pre_request_check falls back to full OAuth if refresh fails."""
    creds = StravaCreds(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token"
    )
    
    with monkeypatch.context() as m:
        mock_refresh = MagicMock(return_value=False)  # Refresh fails
        mock_connect = MagicMock()
        mock_has_valid_token = MagicMock(return_value=False)
        
        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token", 
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) + 3600,
            expires_in=3600,
            refresh_token="fake_refresh"
        )
        m.setattr(StravaClient, "_get_auth_token", MagicMock(return_value=fake_token))
        
        client = StravaClient(creds=creds, auto_reconnect=True)
        m.setattr(client, "_refresh_access_token", mock_refresh)
        m.setattr(client, "connect", mock_connect)
        m.setattr(client, "has_valid_token", mock_has_valid_token)
        
        client._pre_request_check()
        
        # Should try refresh first
        mock_refresh.assert_called_once()
        # Should fall back to connect since refresh failed
        mock_connect.assert_called_once()
