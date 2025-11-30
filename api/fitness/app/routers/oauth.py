import os
from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

# from fitness.load.strava.client import StravaClient
from fitness.db.oauth_credentials import upsert_credentials
from fitness.load.strava.client import StravaCreds
from fitness.integrations import strava


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])
PUBLIC_API_BASE_URL = os.environ["PUBLIC_API_BASE_URL"]


@router.get("/strava/authorize")
def strava_oauth_authorize() -> dict:
    """Log into Strava and redirect to the callback endpoint."""
    url = strava.build_oauth_authorize_url(
        redirect_uri=f"{PUBLIC_API_BASE_URL}/oauth/strava/callback"
    )
    return RedirectResponse(url)


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
    token = await strava.exchange_code_for_token(code)
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
