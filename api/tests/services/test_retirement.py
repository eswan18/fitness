"""Tests for the retirement service."""

from datetime import date

from fitness.services.retirement import RetirementService


def test_retirement_service_initialization():
    """Test that retirement service can be initialized."""
    service = RetirementService()
    # Service should initialize successfully
    assert isinstance(service, RetirementService)


def test_empty_config_file():
    """Test behavior with non-existent config file."""
    service = RetirementService()

    # Should return False for any shoe
    assert not service.is_shoe_retired("Nike Air Zoom")
    assert service.get_retirement_info("Nike Air Zoom") is None
    assert service.list_retired_shoes() == {}


def test_retire_and_check_shoe():
    """Test retiring a shoe and checking its status."""
    service = RetirementService()
    retired_at = date(2024, 12, 15)
    notes = "Worn out after 500 miles"

    # Retire the shoe
    service.retire_shoe("Nike Air Zoom", retired_at, notes)

    # Check retirement status
    assert service.is_shoe_retired("Nike Air Zoom")

    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retired_at == retired_at
    assert info.retirement_notes == notes


def test_unretire_shoe():
    """Test unretiring a shoe."""
    service = RetirementService()
    retired_at = date(2024, 12, 15)

    # Retire then unretire
    service.retire_shoe("Nike Air Zoom", retired_at)
    assert service.is_shoe_retired("Nike Air Zoom")

    was_retired = service.unretire_shoe("Nike Air Zoom")
    assert was_retired is True
    assert not service.is_shoe_retired("Nike Air Zoom")
    assert service.get_retirement_info("Nike Air Zoom") is None


def test_unretire_non_retired_shoe():
    """Test unretiring a shoe that wasn't retired."""
    service = RetirementService()

    was_retired = service.unretire_shoe("Nike Air Zoom")
    assert was_retired is False


def test_list_retired_shoes():
    """Test listing all retired shoes."""
    service = RetirementService()

    # Retire multiple shoes
    service.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Old")
    service.retire_shoe("Brooks Ghost", date(2024, 11, 1), "Worn out")

    retired_shoes = service.list_retired_shoes()
    assert len(retired_shoes) == 2
    assert "Nike Air Zoom" in retired_shoes
    assert "Brooks Ghost" in retired_shoes

    nike_info = retired_shoes["Nike Air Zoom"]
    assert nike_info.retired_at == date(2024, 12, 15)
    assert nike_info.retirement_notes == "Old"


def test_retire_shoe_without_notes():
    """Test retiring a shoe without notes."""
    service = RetirementService()
    retired_at = date(2024, 12, 15)
    
    service.retire_shoe("Nike Air Zoom", retired_at)

    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retired_at == retired_at
    assert info.retirement_notes is None


def test_file_persistence():
    """Test that retirement data persists across service instances."""
    # First service instance
    service1 = RetirementService()
    service1.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Test")

    # Second service instance should load the same data
    service2 = RetirementService()
    assert service2.is_shoe_retired("Nike Air Zoom")
    info = service2.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retirement_notes == "Test"


# Note: test_corrupted_config_file removed as it tested file-based functionality 
# that no longer exists with database storage


# Note: test_config_file_structure removed as it tested file-based functionality
# that no longer exists with database storage


def test_default_config_path():
    """Test that default config path handling works (deprecated but functional)."""
    service = RetirementService()
    # Service should initialize successfully even without config path
    assert isinstance(service, RetirementService)
