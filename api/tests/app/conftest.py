import os
import pytest
from fastapi.testclient import TestClient

from fitness.app.app import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_client() -> TestClient:
    user = os.environ["BASIC_AUTH_USERNAME"]
    password = os.environ["BASIC_AUTH_PASSWORD"]
    client = TestClient(app)
    client.auth = (user, password)
    return client
