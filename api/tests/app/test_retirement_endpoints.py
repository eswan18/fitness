"""Test retirement-related API endpoints."""

import pytest
from fastapi.testclient import TestClient

from fitness.app.app import app
from fitness.models.shoe import generate_shoe_id


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_retire_shoe_endpoint(client, monkeypatch):
    """Test the retire shoe endpoint."""

    # Mock database functions
    def mock_get_shoe_by_id(shoe_id):
        from fitness.models.shoe import Shoe

        return Shoe(id=shoe_id, name="Nike Air Zoom")

    def mock_retire_shoe_by_id(shoe_id, retired_at, retirement_notes):
        return True  # Success

    monkeypatch.setattr("fitness.app.shoe_routes.get_shoe_by_id", mock_get_shoe_by_id)
    monkeypatch.setattr(
        "fitness.app.shoe_routes.retire_shoe_by_id", mock_retire_shoe_by_id
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.patch(
        f"/shoes/{shoe_id}",
        json={
            "retired_at": "2024-12-15",
            "retirement_notes": "Worn out after 500 miles",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Shoe 'Nike Air Zoom' has been retired"}


def test_retire_shoe_without_notes(client, monkeypatch):
    """Test retiring a shoe without notes."""

    # Mock database functions
    def mock_get_shoe_by_id(shoe_id):
        from fitness.models.shoe import Shoe

        return Shoe(id=shoe_id, name="Nike Air Zoom")

    def mock_retire_shoe_by_id(shoe_id, retired_at, retirement_notes):
        return True  # Success

    monkeypatch.setattr("fitness.app.shoe_routes.get_shoe_by_id", mock_get_shoe_by_id)
    monkeypatch.setattr(
        "fitness.app.shoe_routes.retire_shoe_by_id", mock_retire_shoe_by_id
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.patch(f"/shoes/{shoe_id}", json={"retired_at": "2024-12-15"})

    assert response.status_code == 200


def test_unretire_shoe_endpoint(client, monkeypatch):
    """Test the unretire shoe endpoint."""

    # Mock database functions
    def mock_get_shoe_by_id(shoe_id):
        from fitness.models.shoe import Shoe

        return Shoe(id=shoe_id, name="Nike Air Zoom")

    def mock_unretire_shoe_by_id(shoe_id):
        return True  # Success

    monkeypatch.setattr("fitness.app.shoe_routes.get_shoe_by_id", mock_get_shoe_by_id)
    monkeypatch.setattr(
        "fitness.app.shoe_routes.unretire_shoe_by_id", mock_unretire_shoe_by_id
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.patch(f"/shoes/{shoe_id}", json={"retired_at": None})

    assert response.status_code == 200
    assert response.json() == {"message": "Shoe 'Nike Air Zoom' has been unretired"}


def test_unretire_non_retired_shoe(client, monkeypatch):
    """Test unretiring a shoe that was never retired."""

    # Mock database functions
    def mock_get_shoe_by_id(shoe_id):
        from fitness.models.shoe import Shoe

        return Shoe(id=shoe_id, name="Nike Air Zoom")

    def mock_unretire_shoe_by_id(shoe_id):
        return True  # Success (idempotent)

    monkeypatch.setattr("fitness.app.shoe_routes.get_shoe_by_id", mock_get_shoe_by_id)
    monkeypatch.setattr(
        "fitness.app.shoe_routes.unretire_shoe_by_id", mock_unretire_shoe_by_id
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.patch(f"/shoes/{shoe_id}", json={"retired_at": None})

    # With PATCH, this should succeed (idempotent operation)
    assert response.status_code == 200
    assert response.json() == {"message": "Shoe 'Nike Air Zoom' has been unretired"}
