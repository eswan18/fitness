import os
from contextlib import contextmanager
from typing import Iterator

import psycopg


def get_database_url() -> str:
    """Get the database URL from environment variables."""
    url = os.environ["DATABASE_URL"]
    return url


@contextmanager
def get_db_connection() -> Iterator[psycopg.Connection]:
    """Get a database connection context manager."""
    url = get_database_url()
    with psycopg.connect(url) as conn:
        yield conn


@contextmanager
def get_db_cursor() -> Iterator[psycopg.Cursor]:
    """Get a database cursor context manager."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            yield cursor
