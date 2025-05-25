from unittest.mock import MagicMock

import dotenv
import pytest

from fitness.load.strava import StravaClient, StravaCreds, StravaActivity, StravaGear


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
        with pytest.raises(KeyError):
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
