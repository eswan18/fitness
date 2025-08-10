"""Google Calendar API client for syncing workout events."""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import httpx
from fitness.models.run import Run

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""

    def __init__(self):
        """Initialize the client with credentials from environment variables."""
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
        self.refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

        if not all(
            [self.client_id, self.client_secret, self.access_token, self.refresh_token]
        ):
            raise ValueError(
                "Missing Google Calendar credentials. Please set GOOGLE_CLIENT_ID, "
                "GOOGLE_CLIENT_SECRET, GOOGLE_ACCESS_TOKEN, and GOOGLE_REFRESH_TOKEN "
                "environment variables."
            )

        self.base_url = "https://www.googleapis.com/calendar/v3"
        # Allow selecting a specific calendar; default to primary. Some test environments
        # may already have GOOGLE_CALENDAR_ID set; prefer 'primary' when not explicitly provided.
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID") or "primary"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        try:
            with httpx.Client() as client:
                response = client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    logger.info("Successfully refreshed Google access token")
                    return True
                else:
                    logger.error(
                        f"Failed to refresh token: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return False

    def _make_request(
        self, method: str, url: str, **kwargs
    ) -> Optional[httpx.Response]:
        """Make an API request with automatic token refresh on 401."""
        headers = self._get_headers()
        kwargs.setdefault("headers", {}).update(headers)

        try:
            with httpx.Client() as client:
                response = client.request(method, url, **kwargs)

                # If unauthorized, try to refresh token and retry once
                if response.status_code == 401:
                    logger.info("Access token expired, refreshing...")
                    if self._refresh_access_token():
                        # Update headers with new token and retry
                        kwargs["headers"].update(self._get_headers())
                        response = client.request(method, url, **kwargs)
                    else:
                        logger.error("Failed to refresh token, cannot retry request")
                        return response

                return response

        except Exception as e:
            logger.error(f"Error making request to {url}: {e}")
            return None

    def create_workout_event(self, run: Run) -> Optional[str]:
        """Create a calendar event for a workout run.

        Args:
            run: The Run object to create an event for.

        Returns:
            Google Calendar event ID if successful, None otherwise.
        """
        # Format the event title
        distance_str = f"{run.distance:.1f}" if run.distance else "0.0"
        event_title = f"{distance_str} Mile {run.type or 'Run'}"

        # Convert stored UTC-naive datetime to timezone-aware UTC
        start_dt_utc = run.datetime_utc.replace(tzinfo=timezone.utc)

        # Use actual run duration for end time in UTC
        duration_seconds = int(run.duration)
        if duration_seconds < 0:
            duration_seconds = 0
        end_dt_utc = start_dt_utc + timedelta(seconds=duration_seconds)

        event_data = {
            "summary": event_title,
            "description": f"Workout synced from fitness app\nRun ID: {run.id}",
            "start": {
                # RFC3339 with explicit UTC offset
                "dateTime": start_dt_utc.isoformat(),
            },
            "end": {
                "dateTime": end_dt_utc.isoformat(),
            },
        }

        url = f"{self.base_url}/calendars/{self.calendar_id}/events"
        response = self._make_request("POST", url, json=event_data)

        if response and 200 <= response.status_code < 300:
            event = response.json()
            event_id = event.get("id")
            logger.info(f"Created calendar event {event_id} for run {run.id}")
            return event_id
        else:
            error_msg = response.text if response else "No response"
            logger.error(
                f"Failed to create calendar event for run {run.id}: {error_msg}"
            )
            return None

    def delete_workout_event(self, event_id: str) -> bool:
        """Delete a calendar event.

        Args:
            event_id: Google Calendar event ID to delete.

        Returns:
            True if successful, False otherwise.
        """
        url = f"{self.base_url}/calendars/{self.calendar_id}/events/{event_id}"
        response = self._make_request("DELETE", url)

        if response and response.status_code == 204:
            logger.info(f"Deleted calendar event {event_id}")
            return True
        else:
            error_msg = response.text if response else "No response"
            logger.error(f"Failed to delete calendar event {event_id}: {error_msg}")
            return False

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a calendar event by ID.

        Args:
            event_id: Google Calendar event ID.

        Returns:
            Event data dict if successful, None otherwise.
        """
        url = f"{self.base_url}/calendars/{self.calendar_id}/events/{event_id}"
        response = self._make_request("GET", url)

        if response and response.status_code == 200:
            return response.json()
        else:
            error_msg = response.text if response else "No response"
            logger.error(f"Failed to get calendar event {event_id}: {error_msg}")
            return None
