import socket
from typing import Self, Iterable
from io import StringIO
import os
from dataclasses import dataclass
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs
import httpx

AUTH_URL = "https://www.strava.com/oauth/authorize"
AUTH_REFRESH_URL = "https://www.strava.com/oauth/token"
GEAR_URL = "https://www.strava.com/api/v3/gear/"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


@dataclass
class StravaCreds:
    client_id: str
    client_secret: str
    refresh_token: str

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            client_id=os.environ["STRAVA_CLIENT_ID"],
            client_secret=os.environ["STRAVA_CLIENT_SECRET"],
            refresh_token=os.environ["STRAVA_REFRESH_TOKEN"],
        )


@dataclass
class StravaClient:
    creds: StravaCreds
    auth_token: str

    @classmethod
    def from_env(cls) -> Self:
        creds = StravaCreds.from_env()
        auth_token = cls._get_auth_token(creds)
        return cls(creds=creds, auth_token=auth_token)

    def reconnect(self):
        """Reconnect to the Strava API with a fresh auth token."""
        self.auth_token = self._get_auth_token(self.creds)

    @staticmethod
    def _find_open_port() -> int:
        """Find an open port to use for the redirect URI."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @classmethod
    def _get_auth_token(cls, creds: StravaCreds) -> str:
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
        payload["code"] = code
        response = httpx.post(AUTH_REFRESH_URL, data=payload)
        data = response.json()
        return data["access_token"]

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
                code = query_components["code"]
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

    def get_activities(self) -> list["Activity"]:
        """Get the activities from the Strava API."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        page = 1
        per_page = 200
        dfs = []
        while True:
            params = {"per_page": per_page, "page": page}
            response = httpx.get(ACTIVITIES_URL, headers=headers, params=params)
            page += 1
            df = pd.read_json(StringIO(response.text))
            if len(df) == 0:
                break
            dfs.append(df)
        return pd.concat(dfs)

    def get_gear(self, gear_ids: Iterable[str], auth_token: str) -> list["Gear"]:
        records = []
        headers = {"Authorization": f"Bearer {auth_token}"}
        for id in gear_ids:
            response = httpx.get(f"{GEAR_URL}/{id}", headers=headers)
            data = response.json()
            records.append(data)
        return pd.DataFrame(records)
