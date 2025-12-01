from unittest.mock import AsyncMock, MagicMock
import datetime

import pytest
import httpx

from fitness.db.oauth_credentials import OAuthCredentials
from fitness.integrations.strava.client import StravaClient
from fitness.integrations.strava.models import StravaActivity, StravaGear, StravaToken


def test_needs_token_refresh_valid():
    one_hour_from_now = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(hours=1)
    valid_creds = OAuthCredentials(
        provider="strava",
        client_id="123",
        client_secret="456",
        access_token="101",
        refresh_token="789",
        expires_at=one_hour_from_now,
    )
    client = StravaClient(creds=valid_creds)
    assert client.needs_token_refresh() is False


def test_needs_token_refresh_invalid():
    one_minute_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        minutes=1
    )
    invalid_creds = OAuthCredentials(
        provider="strava",
        client_id="123",
        client_secret="456",
        access_token="101",
        refresh_token="789",
        expires_at=one_minute_ago,
    )
    client = StravaClient(creds=invalid_creds)
    assert client.needs_token_refresh() is True


def test_get_activities(real_strava_client: StravaClient):
    activities = real_strava_client.get_activities()
    assert len(activities) > 0
    assert all(isinstance(activity, StravaActivity) for activity in activities)


def test_get_gear(real_strava_client: StravaClient):
    # This is cheating, but I know these two Gear IDs exist in my Strava account
    ids = ["g18184182", "g20299197"]
    gear = real_strava_client.get_gear(ids)
    assert len(gear) == len(ids)
    assert all(isinstance(g, StravaGear) for g in gear)


@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    """Test successful token refresh."""
    now = datetime.datetime.now(datetime.timezone.utc)
    one_minute_ago = now - datetime.timedelta(minutes=1)
    expired_creds = OAuthCredentials(
        provider="strava",
        client_id="123",
        client_secret="456",
        access_token="101",
        refresh_token="789",
        expires_at=one_minute_ago,
    )
    client = StravaClient(creds=expired_creds)

    one_hour_from_now = int((now + datetime.timedelta(hours=1)).timestamp())
    refresh_access_token = AsyncMock(
        return_value=StravaToken(
            token_type="Bearer",
            access_token="new_access_token",
            expires_at=one_hour_from_now,
            expires_in=3600,
            refresh_token="new_refresh_token",
        )
    )
    upsert_credentials = MagicMock()
    with monkeypatch.context() as m:
        m.setattr(
            "fitness.integrations.strava.client.refresh_access_token",
            refresh_access_token,
        )
        m.setattr(
            "fitness.integrations.strava.client.upsert_credentials", upsert_credentials
        )
        await client.refresh_access_token()
    assert refresh_access_token.call_count == 1
    assert upsert_credentials.call_count == 1
    assert client.creds.access_token == "new_access_token"
    assert client.creds.refresh_token == "new_refresh_token"
    assert client.creds.expires_at == one_hour_from_now


def test_refresh_access_token_failure(monkeypatch):
    """Test failed token refresh."""
    creds = StravaCreds(
        client_id="test_client_id",
        client_secret="test_client_secret",
        refresh_token="test_refresh_token",
    )

    with monkeypatch.context() as m:
        # Mock a failed HTTP request
        m.setattr(
            httpx,
            "post",
            MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "", request=MagicMock(), response=MagicMock()
                )
            ),
        )

        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token",
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            + 3600,
            expires_in=3600,
            refresh_token="fake_refresh",
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
        refresh_token="test_refresh_token",
    )

    with monkeypatch.context() as m:
        mock_refresh = MagicMock(return_value=True)
        mock_connect = MagicMock()
        mock_has_valid_token = MagicMock(return_value=False)

        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token",
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            + 3600,
            expires_in=3600,
            refresh_token="fake_refresh",
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
        refresh_token="test_refresh_token",
    )

    with monkeypatch.context() as m:
        mock_refresh = MagicMock(return_value=False)  # Refresh fails
        mock_connect = MagicMock()
        mock_has_valid_token = MagicMock(return_value=False)

        # Mock _get_auth_token to avoid real OAuth flow during init
        fake_token = StravaToken(
            token_type="Bearer",
            access_token="fake_token",
            expires_at=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            + 3600,
            expires_in=3600,
            refresh_token="fake_refresh",
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
