import pandas as pd
import yaml
import httpx
import http.server
import webbrowser
from urllib.parse import urlparse, parse_qs
from io import StringIO

AUTH_URL = "https://www.strava.com/oauth/authorize"
AUTH_REFRESH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

code = None

KEEP_COLS = [
    "type",
    "start_date_local",
    "elapsed_time",
    "distance",
    "gear_id",
]


def _filter_to_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Only keep indoor and outdoor runs."""
    return df[df["type"] == "Run"].copy()


def _convert_km_to_miles(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Distance from meters to miles."""
    df = df.copy()
    df["Distance (mi)"] = df["distance"] / 1609.34
    df = df.drop(columns=["distance"])
    return df


def _remove_unneeded_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limit down to just the columns we need."""
    return df[KEEP_COLS].copy()


def _parse_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the date column."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["start_date_local"])
    df = df.drop(columns=["start_date_local"])
    df["Date"] = df["Date"].dt.tz_localize(None)
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename some columns to match the MMF columns."""
    df = df.copy()
    mapping = {
        "elapsed_time": "Workout Time (seconds)",
        "gear_id": "Shoes",
        # "Calories": "Calories Burned (kCal)",
    }
    for old_name, new_name in mapping.items():
        df[new_name] = df[old_name]
        df.drop(columns=[old_name], inplace=True)
    return df


def _add_source_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column for the source of the data."""
    df = df.copy()
    df["Source"] = "Strava"
    return df


def _rename_shoes(df: pd.DataFrame) -> pd.DataFrame:
    transforms = {
        "Adizero SL": "Adidas Adizero SL",
        "Ghost 15": "Brooks Ghost 15",
        "Pegasus 38": "Nike Air Zoom Pegasus 38",
    }
    df = df.copy()
    df["Shoes"] = df["Shoes"].replace(transforms)
    return df


_cleaning_functions = [
    _filter_to_runs,
    _remove_unneeded_columns,
    _convert_km_to_miles,
    _parse_date,
    _rename_columns,
    _add_source_column,
    _rename_shoes,
]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe."""
    for cleaning_function in _cleaning_functions:
        df = cleaning_function(df)
    return df


def pull_data() -> pd.DataFrame:
    """Pull the data from the Strava CSV."""
    token = _get_auth_token()
    df = _get_activities(token)
    return df


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


def _get_auth_token() -> str:
    """Get the auth token from the environment."""
    with open("secrets.yaml") as f:
        secrets = yaml.safe_load(f)
    params = {
        "client_id": secrets["strava"]["client_id"],
        "response_type": "code",
        "scope": "activity:read_all",
        "redirect_uri": "http://localhost:9384/",
    }
    url = f"{AUTH_URL}?{"&".join(f"{k}={v}" for (k,v) in params.items())}"
    # Open the user's browser to this url
    webbrowser.open(url)
    # Start a tiny webserver to receive the auth code.
    server = http.server.HTTPServer(("localhost", 9384), OAuthCallbackHandler)
    # Run it -- the server
    server.handle_request()
    # The server updates the global variable `code` with the auth code if received.
    if code is None:
        raise ValueError("No code received.")

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


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract the query parameters (assuming the callback contains them)
        query_components = parse_qs(urlparse(self.path).query)
        global code
        code = query_components["code"]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Callback received. You can close this window.")
