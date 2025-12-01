import os
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from fitness.db.oauth_credentials import (
    get_credentials,
    upsert_credentials,
    OAuthIntegrationStatus,
)
from fitness.integrations import strava

PUBLIC_API_BASE_URL = os.environ["PUBLIC_API_BASE_URL"]
PUBLIC_DASHBOARD_BASE_URL = os.environ["PUBLIC_DASHBOARD_BASE_URL"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/strava/status", response_model=OAuthIntegrationStatus)
def strava_auth_status() -> OAuthIntegrationStatus:
    """Get the current authorization status for Strava.

    Returns whether the user has authorized Strava and if the access token is valid.
    """
    creds = get_credentials("strava")
    if creds is None:
        return OAuthIntegrationStatus(authorized=False)
    return creds.integration_status()


@router.get("/strava/authorize")
def strava_oauth_authorize() -> RedirectResponse:
    """Log into Strava and redirect to the callback endpoint."""
    url = strava.build_oauth_authorize_url(
        redirect_uri=f"{PUBLIC_API_BASE_URL}/oauth/strava/callback"
    )
    return RedirectResponse(url)


@router.get("/strava/callback")
async def strava_oauth_callback(
    code: str | None = None, state: str | None = None
) -> RedirectResponse:
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
    # Redirect back to the frontend.
    return RedirectResponse(PUBLIC_DASHBOARD_BASE_URL)
