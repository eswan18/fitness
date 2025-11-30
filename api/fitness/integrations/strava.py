import os
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlencode
import logging

import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from fitness.load.strava.client import StravaCreds

TOKEN_URL = os.environ["STRAVA_TOKEN_URL"]
OAUTH_URL = os.environ["STRAVA_OAUTH_URL"]
PUBLIC_API_BASE_URL = os.environ["PUBLIC_API_BASE_URL"]

logger = logging.getLogger(__name__)


class StravaToken(BaseModel):
    token_type: Literal["Bearer"]
    expires_at: int
    expires_in: int
    refresh_token: str
    access_token: str

    def expires_at_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.expires_at, tz=timezone.utc)


async def exchange_code_for_token(code: str) -> StravaToken:
    creds = StravaCreds.from_env()
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            TOKEN_URL,
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


def build_oauth_authorize_url(redirect_uri: str, state: str | None = None) -> str:
    creds = StravaCreds.from_env()
    params = {
        "client_id": creds.client_id,
        "redirect_uri": redirect_uri,
        "scope": "activity:read_all",
        "response_type": "code",
    }
    if state is not None:
        params["state"] = state
    url = f"{OAUTH_URL}?{urlencode(params)}"
    logger.info(f"Building OAuth authorize URL: {url}")
    return url
