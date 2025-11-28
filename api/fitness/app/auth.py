"""HTTP Basic Authentication for mutation endpoints."""

import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def get_auth_credentials() -> tuple[str, str]:
    """Load authentication credentials from environment variables.

    Returns:
        Tuple of (username, password)

    Raises:
        ValueError: If credentials not configured in environment
    """
    username = os.getenv("BASIC_AUTH_USERNAME")
    password = os.getenv("BASIC_AUTH_PASSWORD")

    if not username or not password:
        raise ValueError(
            "BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD must be set in environment. "
            "Add them to your .env.dev or .env.prod file."
        )

    return username, password


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic Auth credentials against environment variables.

    This dependency can be added to any endpoint that requires authentication.

    Args:
        credentials: HTTP Basic Auth credentials from request header

    Returns:
        The authenticated username on success

    Raises:
        HTTPException: 401 Unauthorized if credentials are invalid
        HTTPException: 500 Internal Server Error if auth not configured
    """
    try:
        expected_username, expected_password = get_auth_credentials()
    except ValueError:
        # Credentials not configured - fail closed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not properly configured on server",
        )

    # Use secrets.compare_digest for timing-attack resistance
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), expected_username.encode("utf8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), expected_password.encode("utf8")
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
