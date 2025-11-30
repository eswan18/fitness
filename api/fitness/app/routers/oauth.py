import os
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from fitness.db.oauth_credentials import get_credentials, upsert_credentials
from fitness.integrations import strava

PUBLIC_API_BASE_URL = os.environ["PUBLIC_API_BASE_URL"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])


class StravaAuthStatus(BaseModel):
    """Status of Strava OAuth authorization."""

    authorized: bool
    access_token_valid: bool | None = None
    expires_at: str | None = None


@router.get("/strava/status", response_model=StravaAuthStatus)
def strava_auth_status() -> StravaAuthStatus:
    """Get the current authorization status for Strava.

    Returns whether the user has authorized Strava and if the access token is valid.
    """
    creds = get_credentials("strava")
    if creds is None:
        return StravaAuthStatus(authorized=False)
    # Check if access token is expired
    access_token_valid = True
    expires_at_iso = None
    if creds.expires_at:
        expires_at_iso = creds.expires_at.isoformat()
        # Compare with current time (both should be timezone-aware)
        now = datetime.now(timezone.utc)
        # Ensure expires_at is timezone-aware
        expires_at_aware = creds.expires_at
        if expires_at_aware.tzinfo is None:
            expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)
        access_token_valid = expires_at_aware > now
    return StravaAuthStatus(
        authorized=True,
        access_token_valid=access_token_valid,
        expires_at=expires_at_iso,
    )


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
    upsert_credentials(
        "strava",
        strava.CLIENT_ID,
        strava.CLIENT_SECRET,
        token.access_token,
        token.refresh_token,
        token.expires_at_datetime(),
    )
    # Redirect back to  the frontend.
    return {"status": "success", "message": "Strava OAuth callback successful"}
