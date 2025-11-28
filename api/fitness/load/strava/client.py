import socket
from typing import Self, Iterable
import os
from dataclasses import dataclass
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime, timezone
import logging
import time

import httpx

from .models import StravaActivity, StravaGear, activity_list_adapter, StravaToken
from fitness.db.oauth_credentials import (
    get_credentials,
    upsert_credentials,
)

logger = logging.getLogger(__name__)

AUTH_URL = "https://www.strava.com/oauth/authorize"
AUTH_REFRESH_URL = "https://www.strava.com/oauth/token"
GEAR_URL = "https://www.strava.com/api/v3/gear"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ATHLETE_URL = "https://www.strava.com/api/v3/athlete"


class StravaClientError(Exception): ...


@dataclass
class StravaCreds:
    client_id: str
    client_secret: str
    refresh_token: str
    access_token: str | None = None
    expires_at: int | None = None
    using_database: bool = False

    @classmethod
    def from_env(cls) -> Self:
        """Load credentials from database first, fall back to environment variables."""
        # Try to load from database first
        db_creds = get_credentials("strava")

        if db_creds:
            logger.info("Loading Strava OAuth credentials from database")
            # Convert datetime to Unix timestamp if needed
            expires_at = None
            if db_creds.expires_at:
                expires_at = int(
                    db_creds.expires_at.replace(tzinfo=timezone.utc).timestamp()
                )
            logger.info(f"Strava credentials loaded from database: {db_creds}, expires_at: {expires_at}")

            return cls(
                client_id=db_creds.client_id,
                client_secret=db_creds.client_secret,
                refresh_token=db_creds.refresh_token,
                access_token=db_creds.access_token,
                expires_at=expires_at,
                using_database=True,
            )

        # Fall back to environment variables
        logger.info(
            "Database credentials not found, loading Strava credentials from environment variables"
        )
        try:
            # Required fields
            creds = cls(
                client_id=os.environ["STRAVA_CLIENT_ID"],
                client_secret=os.environ["STRAVA_CLIENT_SECRET"],
                refresh_token=os.environ["STRAVA_REFRESH_TOKEN"],
                using_database=False,
            )

            # Optional persisted token fields
            if "STRAVA_ACCESS_TOKEN" in os.environ:
                creds.access_token = os.environ["STRAVA_ACCESS_TOKEN"]

            if "STRAVA_EXPIRES_AT" in os.environ:
                try:
                    creds.expires_at = int(os.environ["STRAVA_EXPIRES_AT"])
                except ValueError:
                    # Invalid expires_at, ignore and let it refresh
                    pass

            return creds
        except KeyError as e:
            raise ValueError(
                f"Missing Strava credentials. Please either:\n"
                f"1. Run 'python scripts/migrate_strava_tokens_to_db.py' to migrate existing tokens, or\n"
                f"2. Set required environment variable {e.args[0]}"
            ) from None


@dataclass
class StravaClient:
    creds: StravaCreds
    auto_reconnect: bool = True
    _auth_token: StravaToken | None = None

    def __post_init__(self) -> None:
        if self._auth_token is None:
            # Try to use persisted token first
            if self.creds.access_token and self.creds.expires_at:
                self._auth_token = StravaToken(
                    token_type="Bearer",
                    access_token=self.creds.access_token,
                    expires_at=self.creds.expires_at,
                    expires_in=self.creds.expires_at - int(time.time()),
                    refresh_token=self.creds.refresh_token,
                )

            # If no valid persisted token, connect normally
            if not self.has_valid_token():
                self.connect()

    @classmethod
    def from_env(cls) -> Self:
        creds = StravaCreds.from_env()
        return cls(creds=creds)

    def has_valid_token(self) -> bool:
        """Check if the client's token for the API is valid."""
        if self._auth_token is None:
            return False
        # Trust the expiration time instead of making API calls that can hit rate limits
        return not self._auth_token.is_expired()

    def _auth_headers(self) -> dict[str, str]:
        """Get the headers for the Strava API requests."""
        if self._auth_token is None:
            raise StravaClientError("No auth token found. Call client.connect() first.")
        if self._auth_token.token_type != "Bearer":
            raise StravaClientError(
                f"Invalid token type '{self._auth_token.token_type}'"
            )
        return {"Authorization": f"Bearer {self._auth_token.access_token}"}

    def connect(self) -> None:
        """Get a fresh token for the Strava API."""
        self._auth_token = self._get_auth_token(self.creds)
        # Persist the new token
        self._persist_token(self._auth_token)

    def _refresh_access_token(self) -> bool:
        """Try to refresh the access token using the refresh token.

        Returns:
            bool: True if refresh was successful, False otherwise.
        """
        try:
            payload = {
                "client_id": self.creds.client_id,
                "client_secret": self.creds.client_secret,
                "refresh_token": self.creds.refresh_token,
                "grant_type": "refresh_token",
            }
            response = httpx.post(AUTH_REFRESH_URL, data=payload)
            response.raise_for_status()
            token = StravaToken.model_validate_json(response.content)

            # Update the stored refresh token if a new one was provided
            if token.refresh_token != self.creds.refresh_token:
                self.creds.refresh_token = token.refresh_token

            self._auth_token = token

            # Persist the new token
            self._persist_token(token)

            return True
        except Exception:
            # If refresh fails for any reason, return False so we can fall back to full OAuth
            return False

    @staticmethod
    def _find_open_port() -> int:
        """Find an open port to use for the redirect URI."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @classmethod
    def _get_auth_token(cls, creds: StravaCreds) -> StravaToken:
        """Get the auth token using OAuth browser flow.

        Opens a browser to request user authorization, receives the callback on a
        temporary local HTTP server, then exchanges the code for a token.
        """
        port = cls._find_open_port()
        params = {
            "client_id": creds.client_id,
            "response_type": "code",
            "scope": "activity:read_all",
            "redirect_uri": f"http://localhost:{port}/",
            "approval_prompt": "auto",
        }
        # Properly encode URL parameters to handle special characters
        url = f"{AUTH_URL}?{urlencode(params)}"
        # Open the user's browser to this url.
        webbrowser.open(url)
        # Listen for the callback to the redirect URI and get the code from it.
        code = cls._receive_code(port)

        # Exchange authorization code for access token and refresh token.
        payload = {
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        response = httpx.post(AUTH_REFRESH_URL, data=payload)
        response.raise_for_status()
        token = StravaToken.model_validate_json(response.content)
        return token

    @staticmethod
    def _receive_code(port: int) -> str:
        """Receive a code from an OAuth callback."""
        # The callback handler closes over this variable and sets it if it receives a code.
        code = None

        class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self) -> None:
                # Extract the query parameters (assuming the callback contains them)
                query_components = parse_qs(urlparse(self.path).query)
                nonlocal code
                code_list = query_components.get("code")
                if code_list:
                    code = code_list[0]  # parse_qs returns lists, take first value
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Callback received. You can close this window.")

        server = http.server.HTTPServer(("localhost", port), OAuthCallbackHandler)
        # Handle just one request, then shut down the server.
        server.handle_request()
        if code is not None:
            return code
        else:
            raise ValueError("No code received.")

    def get_activities(self) -> list[StravaActivity]:
        """Get the activities from the Strava API."""
        raw_activities = self._get_activities_raw()
        activities = activity_list_adapter.validate_python(raw_activities)
        return activities

    def _get_activities_raw(self) -> list[dict]:
        """Get the activity data from the Strava API.

        Handles pagination until no more pages are returned.
        """
        self._pre_request_check()
        page = 1
        per_page = 200
        activities: list[dict] = []
        logger.info(f"Fetching activities from Strava API (page size: {per_page})")

        while True:
            params = {"per_page": per_page, "page": page}
            logger.debug(f"Requesting Strava activities page {page}: {params}")

            try:
                response = httpx.get(
                    ACTIVITIES_URL,
                    headers=self._auth_headers(),
                    params=params,
                    timeout=20,  # This request is often *extremely* slow
                )
                response.raise_for_status()
                payload: list[dict] = response.json()

                logger.debug(f"Received {len(payload)} activities from page {page}")
                activities.extend(payload)

                if len(payload) == 0:
                    # This indicates there are no more activities to fetch.
                    logger.info(
                        f"Completed fetching activities: {len(activities)} total activities across {page - 1} pages"
                    )
                    break

                page += 1

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Strava API returned error on page {page}: {e.response.status_code} {e.response.text}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(
                    f"Failed to connect to Strava API on page {page}: {type(e).__name__}: {str(e)}"
                )
                raise

        return activities

    def get_gear(self, gear_ids: Iterable[str]) -> list[StravaGear]:
        """Get the gear from the Strava API."""
        raw_gear = self._get_gear_raw(gear_ids)
        gear = [StravaGear.model_validate(g) for g in raw_gear]
        return gear

    def _get_gear_raw(self, gear_ids: Iterable[str]) -> list[dict]:
        """Get the gear data from the Strava API."""
        self._pre_request_check()
        gear: list[dict] = []
        gear_id_list = list(gear_ids)

        logger.info(f"Fetching {len(gear_id_list)} gear items from Strava API")

        for idx, id in enumerate(gear_id_list, start=1):
            logger.debug(f"Fetching gear {idx}/{len(gear_id_list)}: {id}")

            try:
                response = httpx.get(
                    f"{GEAR_URL}/{id}", headers=self._auth_headers(), timeout=10
                )
                response.raise_for_status()
                payload_gear = response.json()
                gear.append(payload_gear)

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Strava API returned error for gear {id}: {e.response.status_code} {e.response.text}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(
                    f"Failed to fetch gear {id} from Strava API: {type(e).__name__}: {str(e)}"
                )
                raise

        logger.info(f"Successfully fetched {len(gear)} gear items from Strava API")
        return gear

    def _pre_request_check(self) -> None:
        """Check if the token is valid before making a request.

        Will attempt to refresh using the stored refresh token and only fall back
        to a full OAuth flow if refresh fails and `auto_reconnect` is True.
        """
        if not self.has_valid_token():
            if self.auto_reconnect:
                # First try to refresh the token using the refresh token
                if not self._refresh_access_token():
                    # If refresh fails, fall back to full OAuth flow
                    self.connect()
            else:
                raise StravaClientError("Invalid token")

    def _persist_token(self, token: StravaToken) -> None:
        """Update credentials and persist to database if using database credentials.

        Saves tokens to database for persistence across restarts.
        Falls back to in-memory only if using environment variables.
        """
        # Update credentials object in memory
        self.creds.access_token = token.access_token
        self.creds.expires_at = token.expires_at
        self.creds.refresh_token = token.refresh_token

        # Log token refresh for visibility
        expires_time = datetime.fromtimestamp(token.expires_at)

        # Persist to database if using database credentials
        if self.creds.using_database:
            try:
                # Convert Unix timestamp to datetime for database storage
                expires_datetime = datetime.fromtimestamp(
                    token.expires_at, tz=timezone.utc
                )

                upsert_credentials(
                    provider="strava",
                    client_id=self.creds.client_id,
                    client_secret=self.creds.client_secret,
                    access_token=token.access_token,
                    refresh_token=token.refresh_token,
                    expires_at=expires_datetime,
                )
                logger.info(
                    f"🔄 Strava token refreshed and persisted to database (expires: {expires_time})"
                )
            except Exception as db_error:
                logger.error(f"Failed to persist Strava token to database: {db_error}")
                logger.warning(
                    "Token refreshed in memory but not persisted - may need to refresh again on restart"
                )
                print(
                    f"⚠️  Strava token refreshed in memory only (expires: {expires_time})"
                )
        else:
            logger.info(
                f"🔄 Strava token refreshed in memory only (expires: {expires_time})"
            )
            print(f"🔄 Strava token refreshed (expires: {expires_time})")
