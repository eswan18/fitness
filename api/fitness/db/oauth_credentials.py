"""Database operations for OAuth credentials."""

import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from .connection import get_db_cursor, get_db_connection

logger = logging.getLogger(__name__)


@dataclass
class OAuthCredentials:
    """OAuth credentials for a provider."""

    provider: str
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: str
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def get_credentials(provider: str) -> Optional[OAuthCredentials]:
    """Get OAuth credentials for a provider.

    Args:
        provider: Provider name (e.g., 'google')

    Returns:
        OAuthCredentials if found, None otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT provider, client_id, client_secret, access_token, refresh_token,
                   expires_at, created_at, updated_at
            FROM oauth_credentials
            WHERE provider = %s
            """,
            (provider,),
        )

        row = cursor.fetchone()
        if row is None:
            return None

        return OAuthCredentials(
            provider=row[0],
            client_id=row[1],
            client_secret=row[2],
            access_token=row[3],
            refresh_token=row[4],
            expires_at=row[5],
            created_at=row[6],
            updated_at=row[7],
        )


def upsert_credentials(
    provider: str,
    client_id: str,
    client_secret: str,
    access_token: str,
    refresh_token: str,
    expires_at: Optional[datetime] = None,
) -> None:
    """Insert or update OAuth credentials for a provider.

    Args:
        provider: Provider name (e.g., 'google')
        client_id: OAuth client ID
        client_secret: OAuth client secret
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        expires_at: Optional expiration timestamp for access token
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO oauth_credentials
                    (provider, client_id, client_secret, access_token, refresh_token, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider)
                DO UPDATE SET
                    client_id = EXCLUDED.client_id,
                    client_secret = EXCLUDED.client_secret,
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    provider,
                    client_id,
                    client_secret,
                    access_token,
                    refresh_token,
                    expires_at,
                ),
            )
            conn.commit()

    logger.info(f"Upserted OAuth credentials for provider: {provider}")


def update_access_token(
    provider: str,
    access_token: str,
    expires_at: Optional[datetime] = None,
) -> None:
    """Update only the access token for a provider.

    Args:
        provider: Provider name (e.g., 'google')
        access_token: New OAuth access token
        expires_at: Optional expiration timestamp for access token
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE oauth_credentials
                SET access_token = %s,
                    expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE provider = %s
                """,
                (access_token, expires_at, provider),
            )
            conn.commit()

    logger.info(f"Updated access token for provider: {provider}")


def credentials_exist(provider: str) -> bool:
    """Check if credentials exist for a provider.

    Args:
        provider: Provider name (e.g., 'google')

    Returns:
        True if credentials exist, False otherwise
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM oauth_credentials WHERE provider = %s",
            (provider,),
        )
        return cursor.fetchone() is not None
