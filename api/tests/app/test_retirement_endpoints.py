"""Tests for retirement-related API endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from fitness.app.app import app
from fitness.services.retirement import RetirementService
from fitness.models.shoe import generate_shoe_id


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_retire_shoe_endpoint(client, monkeypatch):
    """Test the retire shoe endpoint."""

    # Mock RetirementService to use our temp file
    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.post(
        f"/shoes/{shoe_id}/retire",
        json={"retired_at": "2024-12-15", "retirement_notes": "Worn out after 500 miles"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Shoe 'Nike Air Zoom' has been retired"}

    # Verify the shoe was actually retired
    service = RetirementService()
    assert service.is_shoe_retired("Nike Air Zoom")
    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retired_at == date(2024, 12, 15)
    assert info.retirement_notes == "Worn out after 500 miles"


def test_retire_shoe_without_notes(client, monkeypatch):
    """Test retiring a shoe without notes."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.post(
        f"/shoes/{shoe_id}/retire", json={"retired_at": "2024-12-15"}
    )

    assert response.status_code == 200

    service = RetirementService()
    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retirement_notes is None


def test_unretire_shoe_endpoint(client, monkeypatch):
    """Test the unretire shoe endpoint."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    # First retire the shoe
    service = RetirementService()
    service.retire_shoe("Nike Air Zoom", date(2024, 12, 15))

    # Then unretire it via API
    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.delete(f"/shoes/{shoe_id}/retire")

    assert response.status_code == 200
    assert response.json() == {"message": "Shoe 'Nike Air Zoom' has been unretired"}

    # Verify the shoe was actually unretired
    assert not service.is_shoe_retired("Nike Air Zoom")


def test_unretire_non_retired_shoe(client, monkeypatch):
    """Test unretiring a shoe that was never retired."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    shoe_id = generate_shoe_id("Nike Air Zoom")
    response = client.delete(f"/shoes/{shoe_id}/retire")

    assert response.status_code == 404
    assert "was not retired" in response.json()["detail"]


def test_list_retired_shoes_endpoint(client, monkeypatch):
    """Test the list retired shoes endpoint."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    # Retire some shoes
    service = RetirementService()
    service.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Old")
    service.retire_shoe("Brooks Ghost", date(2024, 11, 1), "Worn out")

    response = client.get("/shoes/?retired=true")

    assert response.status_code == 200
    retired_shoes = response.json()

    assert len(retired_shoes) == 2

    # Find Nike in results
    nike_shoe = next(s for s in retired_shoes if s["name"] == "Nike Air Zoom")
    assert nike_shoe["retired_at"] == "2024-12-15"
    assert nike_shoe["retirement_notes"] == "Old"

    # Find Brooks in results
    brooks_shoe = next(s for s in retired_shoes if s["name"] == "Brooks Ghost")
    assert brooks_shoe["retired_at"] == "2024-11-01"
    assert brooks_shoe["retirement_notes"] == "Worn out"


def test_list_retired_shoes_empty(client, monkeypatch):
    """Test listing retired shoes when none are retired."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr(
        "fitness.app.shoe_routes.RetirementService", mock_retirement_service
    )

    response = client.get("/shoes/?retired=true")

    assert response.status_code == 200
    assert response.json() == []


def test_mileage_by_shoe_with_include_retired_param(
    client, monkeypatch
):
    """Test the mileage by shoe endpoint with include_retired parameter."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr("fitness.agg.shoes.RetirementService", mock_retirement_service)

    # This test assumes we have some run data loaded
    # Test default behavior (exclude retired)
    response = client.get("/metrics/mileage/by-shoe")
    assert response.status_code == 200

    # Test include retired
    response = client.get("/metrics/mileage/by-shoe?include_retired=true")
    assert response.status_code == 200

    # Test explicitly exclude retired
    response = client.get("/metrics/mileage/by-shoe?include_retired=false")
    assert response.status_code == 200


def test_mileage_by_shoe_with_retirement_endpoint(
    client, monkeypatch
):
    """Test the mileage by shoe with retirement info endpoint."""

    def mock_retirement_service():
        return RetirementService()

    monkeypatch.setattr("fitness.agg.shoes.RetirementService", mock_retirement_service)

    response = client.get("/metrics/mileage/by-shoe-with-retirement")
    assert response.status_code == 200

    # Should return list of ShoeMileageWithRetirement objects
    shoes = response.json()
    assert isinstance(shoes, list)

    # Each shoe should have the required fields
    for shoe in shoes:
        assert "shoe" in shoe
        assert "mileage" in shoe
        assert "retired" in shoe
        assert "retired_at" in shoe or shoe["retired_at"] is None
        assert "retirement_notes" in shoe or shoe["retirement_notes"] is None
