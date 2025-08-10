"""Tests for Google Calendar client."""

import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest
import httpx

from fitness.google.calendar_client import GoogleCalendarClient
from fitness.models.run import Run


class TestGoogleCalendarClientInit:
    """Test GoogleCalendarClient initialization."""

    def test_init_with_all_credentials(self):
        """Test client initializes properly with all required credentials."""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test_client_id",
                "GOOGLE_CLIENT_SECRET": "test_client_secret",
                "GOOGLE_ACCESS_TOKEN": "test_access_token",
                "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
            },
            clear=True,
        ):
            client = GoogleCalendarClient()
            assert client.client_id == "test_client_id"
            assert client.client_secret == "test_client_secret"
            assert client.access_token == "test_access_token"
            assert client.refresh_token == "test_refresh_token"
            assert client.base_url == "https://www.googleapis.com/calendar/v3"
            assert client.calendar_id == "primary"

    def test_init_missing_credentials(self):
        """Test client raises error when credentials are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing Google Calendar credentials"):
                GoogleCalendarClient()

    def test_init_partial_credentials(self):
        """Test client raises error when only some credentials are provided."""
        with patch.dict(
            os.environ,
            {
                "GOOGLE_CLIENT_ID": "test_client_id",
                "GOOGLE_CLIENT_SECRET": "test_client_secret",
            },
            clear=True,
        ):
            with pytest.raises(ValueError, match="Missing Google Calendar credentials"):
                GoogleCalendarClient()


class TestGoogleCalendarClientHeaders:
    """Test header generation."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    def test_get_headers(self):
        """Test headers are generated correctly."""
        client = GoogleCalendarClient()
        headers = client._get_headers()

        expected_headers = {
            "Authorization": "Bearer test_access_token",
            "Content-Type": "application/json",
        }
        assert headers == expected_headers


class TestGoogleCalendarClientTokenRefresh:
    """Test token refresh functionality."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "old_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_refresh_access_token_success(self, mock_client):
        """Test successful token refresh."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response

        client = GoogleCalendarClient()
        result = client._refresh_access_token()

        assert result is True
        assert client.access_token == "new_access_token"

        # Verify the request was made correctly
        mock_client_instance.post.assert_called_once_with(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "refresh_token": "test_refresh_token",
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "old_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_refresh_access_token_failure(self, mock_client):
        """Test token refresh failure."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response

        client = GoogleCalendarClient()
        old_token = client.access_token
        result = client._refresh_access_token()

        assert result is False
        assert client.access_token == old_token  # Should remain unchanged

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "old_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_refresh_access_token_exception(self, mock_client):
        """Test token refresh with network exception."""
        mock_client.return_value.__enter__.side_effect = httpx.RequestError(
            "Network error"
        )

        client = GoogleCalendarClient()
        result = client._refresh_access_token()

        assert result is False


class TestGoogleCalendarClientMakeRequest:
    """Test the _make_request method."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_make_request_success(self, mock_client):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "event123"}

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        response = client._make_request("GET", "https://test.com/api")

        assert response == mock_response
        mock_client_instance.request.assert_called_once_with(
            "GET",
            "https://test.com/api",
            headers={
                "Authorization": "Bearer test_access_token",
                "Content-Type": "application/json",
            },
        )

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "expired_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_make_request_401_with_successful_refresh(self, mock_client):
        """Test API request with 401 that successfully refreshes token."""
        # First response is 401 (expired token)
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Second response is 200 (after refresh)
        mock_200_response = Mock()
        mock_200_response.status_code = 200
        mock_200_response.json.return_value = {"id": "event123"}

        # Mock token refresh response
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {"access_token": "new_access_token"}

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        # First call returns 401, second call for refresh returns 200, third call returns 200
        mock_client_instance.request.side_effect = [
            mock_401_response,
            mock_200_response,
        ]
        mock_client_instance.post.return_value = mock_token_response

        client = GoogleCalendarClient()
        response = client._make_request("GET", "https://test.com/api")

        assert response == mock_200_response
        assert client.access_token == "new_access_token"

        # Should have made two request calls (original + retry)
        assert mock_client_instance.request.call_count == 2

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "expired_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_make_request_401_with_failed_refresh(self, mock_client):
        """Test API request with 401 and failed token refresh."""
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Mock failed token refresh
        mock_token_response = Mock()
        mock_token_response.status_code = 400
        mock_token_response.text = "Invalid refresh token"

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_401_response
        mock_client_instance.post.return_value = mock_token_response

        client = GoogleCalendarClient()
        response = client._make_request("GET", "https://test.com/api")

        assert response == mock_401_response  # Should return the original 401


class TestGoogleCalendarClientCreateEvent:
    """Test event creation functionality."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_create_workout_event_success(self, mock_client):
        """Test successful workout event creation."""
        # Create a test run
        run = Run(
            id="test_run_123",
            datetime_utc=datetime(2025, 8, 9, 14, 30, 0, tzinfo=timezone.utc),
            type="Outdoor Run",
            distance=5.2,
            duration=2400.0,
            source="Strava",
        )

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "google_event_123",
            "summary": "5.2 Mile Outdoor Run",
        }

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        event_id = client.create_workout_event(run)

        assert event_id == "google_event_123"

        # Verify the request was made correctly
        call_args = mock_client_instance.request.call_args
        assert call_args[0][0] == "POST"  # method
        # Should default to primary calendar when GOOGLE_CALENDAR_ID is not set
        assert (
            call_args[0][1]
            == "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        )

        # Check event data
        event_data = call_args[1]["json"]
        assert event_data["summary"] == "5.2 Mile Outdoor Run"
        assert "Workout synced from fitness app" in event_data["description"]
        assert "Run ID: test_run_123" in event_data["description"]
        assert event_data["colorId"] == "4"
        # When using RFC3339 datetimes with explicit UTC offset, timeZone is optional
        assert "dateTime" in event_data["start"]
        assert event_data["start"]["dateTime"].endswith("+00:00") or event_data["start"][
            "dateTime"
        ].endswith("Z")

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_create_workout_event_with_zero_distance(self, mock_client):
        """Test event creation with zero distance."""
        run = Run(
            id="test_run_123",
            datetime_utc=datetime(2025, 8, 9, 14, 30, 0, tzinfo=timezone.utc),
            type="Treadmill Run",
            distance=0.0,
            duration=1800.0,
            source="Strava",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "google_event_123"}

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        event_id = client.create_workout_event(run)

        assert event_id == "google_event_123"

        # Check that zero distance is formatted correctly
        call_args = mock_client_instance.request.call_args
        event_data = call_args[1]["json"]
        assert event_data["summary"] == "0.0 Mile Treadmill Run"

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_create_workout_event_failure(self, mock_client):
        """Test failed event creation."""
        run = Run(
            id="test_run_123",
            datetime_utc=datetime(2025, 8, 9, 14, 30, 0, tzinfo=timezone.utc),
            type="Outdoor Run",
            distance=5.2,
            duration=2400.0,
            source="Strava",
        )

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid event data"

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        event_id = client.create_workout_event(run)

        assert event_id is None

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_create_workout_event_no_response(self, mock_client):
        """Test event creation with no response."""
        run = Run(
            id="test_run_123",
            datetime_utc=datetime(2025, 8, 9, 14, 30, 0, tzinfo=timezone.utc),
            type="Outdoor Run",
            distance=5.2,
            duration=2400.0,
            source="Strava",
        )

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = None

        client = GoogleCalendarClient()
        event_id = client.create_workout_event(run)

        assert event_id is None


class TestGoogleCalendarClientDeleteEvent:
    """Test event deletion functionality."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
        clear=True,
    )
    @patch("httpx.Client")
    def test_delete_workout_event_success(self, mock_client):
        """Test successful event deletion."""
        mock_response = Mock()
        mock_response.status_code = (
            204  # Google Calendar returns 204 for successful deletion
        )

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        result = client.delete_workout_event("google_event_123")

        assert result is True

        # Verify the request was made correctly
        # Should default to primary calendar when GOOGLE_CALENDAR_ID is not set
        mock_client_instance.request.assert_called_once_with(
            "DELETE",
            "https://www.googleapis.com/calendar/v3/calendars/primary/events/google_event_123",
            headers={
                "Authorization": "Bearer test_access_token",
                "Content-Type": "application/json",
            },
        )

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_delete_workout_event_failure(self, mock_client):
        """Test failed event deletion."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Event not found"

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        result = client.delete_workout_event("nonexistent_event")

        assert result is False


class TestGoogleCalendarClientGetEvent:
    """Test event retrieval functionality."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_get_event_success(self, mock_client):
        """Test successful event retrieval."""
        expected_event = {
            "id": "google_event_123",
            "summary": "5.2 Mile Outdoor Run",
            "start": {"dateTime": "2025-08-09T07:00:00"},
            "end": {"dateTime": "2025-08-09T08:00:00"},
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_event

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        event = client.get_event("google_event_123")

        assert event == expected_event

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test_client_id",
            "GOOGLE_CLIENT_SECRET": "test_client_secret",
            "GOOGLE_ACCESS_TOKEN": "test_access_token",
            "GOOGLE_REFRESH_TOKEN": "test_refresh_token",
        },
    )
    @patch("httpx.Client")
    def test_get_event_not_found(self, mock_client):
        """Test event retrieval for non-existent event."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Event not found"

        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.request.return_value = mock_response

        client = GoogleCalendarClient()
        event = client.get_event("nonexistent_event")

        assert event is None
