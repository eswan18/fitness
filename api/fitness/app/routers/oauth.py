import os
from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx

# from fitness.load.strava.client import StravaClient
from fitness.db.oauth_credentials import upsert_credentials
from fitness.load.strava.client import StravaClient, StravaCreds, oauth_authorize_params

STRAVA_OAUTH_URL = os.environ["STRAVA_OAUTH_URL"]
STRAVA_TOKEN_URL = os.environ["STRAVA_TOKEN_URL"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])
PUBLIC_API_BASE_URL = os.environ["PUBLIC_API_BASE_URL"]


@router.get("/strava/authorize")
def strava_oauth_authorize() -> dict:
    """Log into Strava and redirect to the callback endpoint."""
    client = StravaCreds.from_env()
    params = oauth_authorize_params(
        client_id=client.client_id,
        redirect_uri=f"{PUBLIC_API_BASE_URL}/oauth/strava/callback",
        state="abc",
    )
    auth_url = f"{STRAVA_OAUTH_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/strava/callback")
async def strava_oauth_callback(
    code: str | None = None, state: str | None = None
) -> dict:
    """Strava OAuth callback endpoint."""
    if code is None:
        raise HTTPException(
            status_code=400,
            detail="No code provided",
        )
    token = await _exchange_code_for_token(code)
    # Store the token in the db.
    creds = StravaCreds.from_env()
    upsert_credentials(
        "strava",
        creds.client_id,
        creds.client_secret,
        token.access_token,
        token.refresh_token,
        token.expires_at_datetime(),
    )
    # Redirect back to  the frontend.
    return {"status": "success", "message": "Strava OAuth callback successful"}


class StravaToken(BaseModel):
    token_type: Literal["Bearer"]
    expires_at: int
    expires_in: int
    refresh_token: str
    access_token: str

    def expires_at_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.expires_at, tz=timezone.utc)


async def _exchange_code_for_token(code: str) -> StravaToken:
    creds = StravaCreds.from_env()
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{PUBLIC_API_BASE_URL}/oauth/strava/callback",
            },
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to exchange Strava code (status {response.status_code})",
        )
    return StravaToken.model_validate_json(response.content)
