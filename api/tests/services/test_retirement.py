"""Tests for the retirement service."""

import json
import tempfile
from datetime import date
from pathlib import Path

import pytest

from fitness.services.retirement import RetirementService, ShoeRetirementInfo


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = Path(f.name)
    yield config_path
    # Cleanup
    if config_path.exists():
        config_path.unlink()


def test_retirement_service_initialization(temp_config_file):
    """Test that retirement service can be initialized."""
    service = RetirementService(temp_config_file)
    assert service.config_path == temp_config_file


def test_empty_config_file(temp_config_file):
    """Test behavior with non-existent config file."""
    service = RetirementService(temp_config_file)
    
    # Should return False for any shoe
    assert not service.is_shoe_retired("Nike Air Zoom")
    assert service.get_retirement_info("Nike Air Zoom") is None
    assert service.list_retired_shoes() == {}


def test_retire_and_check_shoe(temp_config_file):
    """Test retiring a shoe and checking its status."""
    service = RetirementService(temp_config_file)
    retirement_date = date(2024, 12, 15)
    notes = "Worn out after 500 miles"
    
    # Retire the shoe
    service.retire_shoe("Nike Air Zoom", retirement_date, notes)
    
    # Check retirement status
    assert service.is_shoe_retired("Nike Air Zoom")
    
    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retirement_date == retirement_date
    assert info.notes == notes


def test_unretire_shoe(temp_config_file):
    """Test unretiring a shoe."""
    service = RetirementService(temp_config_file)
    retirement_date = date(2024, 12, 15)
    
    # Retire then unretire
    service.retire_shoe("Nike Air Zoom", retirement_date)
    assert service.is_shoe_retired("Nike Air Zoom")
    
    was_retired = service.unretire_shoe("Nike Air Zoom")
    assert was_retired is True
    assert not service.is_shoe_retired("Nike Air Zoom")
    assert service.get_retirement_info("Nike Air Zoom") is None


def test_unretire_non_retired_shoe(temp_config_file):
    """Test unretiring a shoe that wasn't retired."""
    service = RetirementService(temp_config_file)
    
    was_retired = service.unretire_shoe("Nike Air Zoom")
    assert was_retired is False


def test_list_retired_shoes(temp_config_file):
    """Test listing all retired shoes."""
    service = RetirementService(temp_config_file)
    
    # Retire multiple shoes
    service.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Old")
    service.retire_shoe("Brooks Ghost", date(2024, 11, 1), "Worn out")
    
    retired_shoes = service.list_retired_shoes()
    assert len(retired_shoes) == 2
    assert "Nike Air Zoom" in retired_shoes
    assert "Brooks Ghost" in retired_shoes
    
    nike_info = retired_shoes["Nike Air Zoom"]
    assert nike_info.retirement_date == date(2024, 12, 15)
    assert nike_info.notes == "Old"


def test_retire_shoe_without_notes(temp_config_file):
    """Test retiring a shoe without notes."""
    service = RetirementService(temp_config_file)
    retirement_date = date(2024, 12, 15)
    
    service.retire_shoe("Nike Air Zoom", retirement_date)
    
    info = service.get_retirement_info("Nike Air Zoom")
    assert info is not None
    assert info.retirement_date == retirement_date
    assert info.notes is None


def test_file_persistence(temp_config_file):
    """Test that retirement data persists across service instances."""
    # First service instance
    service1 = RetirementService(temp_config_file)
    service1.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Test")
    
    # Second service instance should load the same data
    service2 = RetirementService(temp_config_file)
    assert service2.is_shoe_retired("Nike Air Zoom")
    info = service2.get_retirement_info("Nike Air Zoom")
    assert info.notes == "Test"


def test_corrupted_config_file(temp_config_file):
    """Test behavior with corrupted config file."""
    # Write invalid JSON to the file
    with open(temp_config_file, 'w') as f:
        f.write("invalid json content")
    
    service = RetirementService(temp_config_file)
    
    # Should handle gracefully and return empty state
    assert not service.is_shoe_retired("Nike Air Zoom")
    assert service.list_retired_shoes() == {}
    
    # Should still be able to retire shoes (overwrites corrupted file)
    service.retire_shoe("Nike Air Zoom", date(2024, 12, 15))
    assert service.is_shoe_retired("Nike Air Zoom")


def test_config_file_structure():
    """Test the exact structure of the saved JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = Path(f.name)
    
    try:
        service = RetirementService(config_path)
        service.retire_shoe("Nike Air Zoom", date(2024, 12, 15), "Test notes")
        
        # Read the file directly and check structure
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        expected = {
            "Nike Air Zoom": {
                "retirement_date": "2024-12-15",
                "notes": "Test notes"
            }
        }
        assert data == expected
        
    finally:
        if config_path.exists():
            config_path.unlink()


def test_default_config_path():
    """Test that default config path is created correctly."""
    service = RetirementService()
    # Should point to the version-controlled location in the repo
    assert service.config_path.name == "retired-shoes.json"
    assert service.config_path.parent.name == "data"
    assert "api" in str(service.config_path)