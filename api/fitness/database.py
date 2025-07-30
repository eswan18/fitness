"""Database connection and session management."""

import os
from functools import lru_cache
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session


@lru_cache()
def get_database_url() -> str:
    """Get the database URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please set it to a valid PostgreSQL connection string."
        )
    return database_url


@lru_cache()
def get_engine():
    """Get a cached database engine instance."""
    database_url = get_database_url()
    
    # Create engine with recommended settings for PostgreSQL
    engine = create_engine(
        database_url,
        # Connection pool settings
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        # Logging (set to True for debugging)
        echo=False,
    )
    return engine


def create_tables():
    """Create all database tables. Should be called during app startup."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency to get a database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


def get_session_context() -> Session:
    """Get a database session for use outside of FastAPI dependency injection."""
    engine = get_engine()
    return Session(engine)