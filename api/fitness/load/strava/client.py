import socket
from typing import Self, Iterable
import os
from dataclasses import dataclass
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs

import httpx

from .models import StravaActivity, StravaGear, activity_list_adapter, StravaToken

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

    @classmethod
    def from_env(cls) -> Self:
        try:
            return cls(
                client_id=os.environ["STRAVA_CLIENT_ID"],
                client_secret=os.environ["STRAVA_CLIENT_SECRET"],
                refresh_token=os.environ["STRAVA_REFRESH_TOKEN"],
            )
        except KeyError as e:
            raise ValueError(
                f"Required Strava environment variable {e.args[0]} is not set"
            ) from None


@dataclass
class StravaClient:
    creds: StravaCreds
    auto_reconnect: bool = True
    _auth_token: StravaToken | None = None

    def __post_init__(self):
        if self._auth_token is None:
            self.connect()

    @classmethod
    def from_env(cls) -> Self:
        creds = StravaCreds.from_env()
        return cls(creds=creds)

    def has_valid_token(self) -> bool:
        """Check if the client's token for the API is valid."""
        if self._auth_token is None:
            return False
        if self._auth_token.is_expired():
            return False
        # If we have an auth token, we need to make sure it's valid. We make a request
        # to the Strava API to check if the token works.
        response = httpx.get(ATHLETE_URL, headers=self._auth_headers())
        if response.status_code == 401:
            return False
        elif response.status_code == 200:
            return True
        else:
            raise StravaClientError(f"Unexpected status code: {response.status_code}")

    def _auth_headers(self) -> dict[str, str]:
        """Get the headers for the Strava API requests."""
        if self._auth_token is None:
            raise StravaClientError("No auth token found. Call client.connect() first.")
        if self._auth_token.token_type != "Bearer":
            raise StravaClientError(
                f"Invalid token type '{self._auth_token.token_type}'"
            )
        return {"Authorization": f"Bearer {self._auth_token.access_token}"}

    def connect(self):
        """Get a fresh token for the Strava API."""
        self._auth_token = self._get_auth_token(self.creds)

    @staticmethod
    def _find_open_port() -> int:
        """Find an open port to use for the redirect URI."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @classmethod
    def _get_auth_token(cls, creds: StravaCreds) -> StravaToken:
        """Get the auth token from the environment."""
        port = cls._find_open_port()
        params = {
            "client_id": creds.client_id,
            "response_type": "code",
            "scope": "activity:read_all",
            "redirect_uri": f"http://localhost:{port}/",
        }
        # This looks wrong to me ... I think I should use urllib or something else to handle escaping.
        url = f"{AUTH_URL}?{'&'.join(f'{k}={v}' for (k, v) in params.items())}"
        # Open the user's browser to this url.
        webbrowser.open(url)
        # Listen for the callback to the redirect URI and get the code from it.
        code = cls._receive_code(port)

        # Get refresh token.
        payload = {
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "refresh_token": creds.refresh_token,
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
            def do_GET(self):
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
        """Get the activity data from the Strava API."""
        self._pre_request_check()
        page = 1
        per_page = 200
        activities: list[dict] = []
        while True:
            params = {"per_page": per_page, "page": page}
            print("sending request to Strava API for activities", params)
            response = httpx.get(
                ACTIVITIES_URL,
                headers=self._auth_headers(),
                params=params,
                timeout=20,  # This request is often *extremely* slow
            )
            response.raise_for_status()
            payload: list[dict] = response.json()
            activities.extend(payload)
            if len(payload) == 0:
                # This indicates there are no more activities to fetch.
                break
            page += 1
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
        for id in gear_ids:
            response = httpx.get(f"{GEAR_URL}/{id}", headers=self._auth_headers())
            response.raise_for_status()
            payload_gear = response.json()
            gear.append(payload_gear)
        return gear

    def _pre_request_check(self):
        """Check if the token is valid before making a request."""
        if not self.has_valid_token():
            if self.auto_reconnect:
                self.connect()
            else:
                raise StravaClientError("Invalid token")
