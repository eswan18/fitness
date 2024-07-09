from typing import Iterable
import http.server
import webbrowser
from urllib.parse import urlparse, parse_qs
from io import StringIO

import pandas as pd
import yaml
import httpx

AUTH_URL = "https://www.strava.com/oauth/authorize"
AUTH_REFRESH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
GEAR_URL = "https://www.strava.com/api/v3/gear/"
# A random port number I chose just for availability.
PORT = 9384


def pull_data() -> pd.DataFrame:
    """Pull the data from the Strava API."""
    token = _get_auth_token()
    activities = _get_activities(token)
    gear_ids = activities["gear_id"]
    gear_ids = gear_ids[~gear_ids.isnull()].unique()
    gear = _get_gear(gear_ids, token)
    # Turn the gear into a mapping from ID to nickname.
    gear_map = {row["id"]: row["nickname"] for _, row in gear.iterrows()}
    # Add a "Shoes" column to the activities dataframe.
    activities["shoes"] = activities["gear_id"].map(gear_map)
    activities = activities.drop(columns=["gear_id"])
    return activities


def _get_activities(auth_token: str) -> pd.DataFrame:
    """Get the activities from the Strava API."""
    headers = {"Authorization": f"Bearer {auth_token}"}
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


def _get_gear(gear_ids: Iterable[str], auth_token: str) -> pd.DataFrame:
    records = []
    headers = {"Authorization": f"Bearer {auth_token}"}
    for id in gear_ids:
        response = httpx.get(f"{GEAR_URL}/{id}", headers=headers)
        data = response.json()
        records.append(data)
    return pd.DataFrame(records)


def _get_auth_token() -> str:
    """Get the auth token from the environment."""
    with open("secrets.yaml") as f:
        secrets = yaml.safe_load(f)
    params = {
        "client_id": secrets["strava"]["client_id"],
        "response_type": "code",
        "scope": "activity:read_all",
        "redirect_uri": f"http://localhost:{PORT}/",
    }
    url = f"{AUTH_URL}?{"&".join(f"{k}={v}" for (k,v) in params.items())}"
    # Open the user's browser to this url.
    webbrowser.open(url)
    code = _receive_code(PORT)

    # Get refresh token.
    payload = {
        "client_id": secrets["strava"]["client_id"],
        "client_secret": secrets["strava"]["client_secret"],
        "refresh_token": secrets["strava"]["refresh_token"],
        "code": code,
        "grant_type": "authorization_code",
    }
    payload["code"] = code
    response = httpx.post(AUTH_REFRESH_URL, data=payload)
    data = response.json()
    return data["access_token"]


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
