import os
from pathlib import Path
from typing import Iterator
import pytest
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command
from fastapi.testclient import TestClient

# Ensure allowed environment for env_loader
os.environ.setdefault("ENV", "dev")


@pytest.fixture(scope="session")
def db_url() -> Iterator[str]:
    """Start a Postgres container, run migrations, and return the DB URL."""
    with PostgresContainer("postgres:16") as pg:
        raw_url = pg.get_connection_url()
        # Normalize to psycopg3-compatible URL if needed
        url = raw_url.replace("postgresql+psycopg2://", "postgresql://")
        os.environ["DATABASE_URL"] = url

        # Run Alembic migrations against this database
        api_dir = Path(__file__).resolve().parents[2]
        alembic_cfg = Config(str(api_dir / "alembic.ini"))
        command.upgrade(alembic_cfg, "head")

        yield url


@pytest.fixture(scope="session")
def client(db_url: str) -> TestClient:
    """Create a FastAPI TestClient after DB is configured."""
    from fitness.app.app import app

    return TestClient(app)
