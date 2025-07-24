"""Tests for the retirement service."""

import pytest
import json
import tempfile
import threading
import time
from datetime import date
from pathlib import Path
from unittest.mock import patch, mock_open

from fitness.services.retirement import RetirementService, ShoeRetirementInfo


class TestRetirementService:
    """Test the shoe retirement service."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    @pytest.fixture
    def service_with_temp_file(self, temp_config_file):
        """Create a retirement service with a temporary config file."""
        return RetirementService(config_path=temp_config_file)

    def test_init_default_path(self):
        """Test that default path is correctly set."""
        service = RetirementService()
        assert service.config_path.name == "retired-shoes.json"
        assert "data" in str(service.config_path)

    def test_init_custom_path(self, temp_config_file):
        """Test initialization with custom path."""
        service = RetirementService(config_path=temp_config_file)
        assert service.config_path == temp_config_file

    def test_load_empty_file(self, service_with_temp_file):
        """Test loading when file doesn't exist."""
        retired_shoes = service_with_temp_file._load_retired_shoes()
        assert retired_shoes == {}

    def test_save_and_load_retired_shoes(self, service_with_temp_file):
        """Test saving and loading retired shoes."""
        # Prepare test data
        retired_shoes = {
            "Nike Pegasus": ShoeRetirementInfo(
                retirement_date=date(2024, 1, 15),
                notes="Worn out after 500 miles"
            ),
            "Adidas Ultra": ShoeRetirementInfo(
                retirement_date=date(2024, 2, 1),
                notes=None
            )
        }
        
        # Save
        service_with_temp_file._save_retired_shoes(retired_shoes)
        
        # Load and verify
        loaded = service_with_temp_file._load_retired_shoes()
        assert len(loaded) == 2
        assert "Nike Pegasus" in loaded
        assert loaded["Nike Pegasus"].retirement_date == date(2024, 1, 15)
        assert loaded["Nike Pegasus"].notes == "Worn out after 500 miles"
        assert loaded["Adidas Ultra"].retirement_date == date(2024, 2, 1)
        assert loaded["Adidas Ultra"].notes is None

    def test_load_corrupted_file(self, temp_config_file):
        """Test loading a corrupted JSON file."""
        # Write corrupted JSON
        with open(temp_config_file, 'w') as f:
            f.write("{invalid json")
        
        service = RetirementService(config_path=temp_config_file)
        retired_shoes = service._load_retired_shoes()
        assert retired_shoes == {}

    def test_is_shoe_retired(self, service_with_temp_file):
        """Test checking if a shoe is retired."""
        # Initially not retired
        assert not service_with_temp_file.is_shoe_retired("Nike Pegasus")
        
        # Retire the shoe
        service_with_temp_file.retire_shoe("Nike Pegasus", date(2024, 1, 15))
        
        # Now it should be retired
        assert service_with_temp_file.is_shoe_retired("Nike Pegasus")
        assert not service_with_temp_file.is_shoe_retired("Other Shoe")

    def test_get_retirement_info(self, service_with_temp_file):
        """Test getting retirement information."""
        # No info initially
        assert service_with_temp_file.get_retirement_info("Nike Pegasus") is None
        
        # Retire the shoe
        service_with_temp_file.retire_shoe(
            "Nike Pegasus", 
            date(2024, 1, 15),
            notes="Worn out"
        )
        
        # Get info
        info = service_with_temp_file.get_retirement_info("Nike Pegasus")
        assert info is not None
        assert info.retirement_date == date(2024, 1, 15)
        assert info.notes == "Worn out"

    def test_retire_shoe(self, service_with_temp_file):
        """Test retiring a shoe."""
        service_with_temp_file.retire_shoe(
            "Nike Pegasus",
            date(2024, 1, 15),
            notes="500 miles reached"
        )
        
        # Verify it was saved
        retired_shoes = service_with_temp_file._load_retired_shoes()
        assert "Nike Pegasus" in retired_shoes
        assert retired_shoes["Nike Pegasus"].retirement_date == date(2024, 1, 15)
        assert retired_shoes["Nike Pegasus"].notes == "500 miles reached"

    def test_retire_shoe_overwrites(self, service_with_temp_file):
        """Test that retiring a shoe twice overwrites the first retirement."""
        # First retirement
        service_with_temp_file.retire_shoe(
            "Nike Pegasus",
            date(2024, 1, 15),
            notes="First retirement"
        )
        
        # Second retirement
        service_with_temp_file.retire_shoe(
            "Nike Pegasus",
            date(2024, 2, 1),
            notes="Second retirement"
        )
        
        # Should have the second retirement info
        info = service_with_temp_file.get_retirement_info("Nike Pegasus")
        assert info.retirement_date == date(2024, 2, 1)
        assert info.notes == "Second retirement"

    def test_unretire_shoe(self, service_with_temp_file):
        """Test unretiring a shoe."""
        # Retire first
        service_with_temp_file.retire_shoe("Nike Pegasus", date(2024, 1, 15))
        assert service_with_temp_file.is_shoe_retired("Nike Pegasus")
        
        # Unretire
        result = service_with_temp_file.unretire_shoe("Nike Pegasus")
        assert result is True
        assert not service_with_temp_file.is_shoe_retired("Nike Pegasus")
        
        # Try to unretire again
        result = service_with_temp_file.unretire_shoe("Nike Pegasus")
        assert result is False

    def test_list_retired_shoes(self, service_with_temp_file):
        """Test listing all retired shoes."""
        # Initially empty
        assert service_with_temp_file.list_retired_shoes() == {}
        
        # Add some retired shoes
        service_with_temp_file.retire_shoe("Nike Pegasus", date(2024, 1, 15), "Worn out")
        service_with_temp_file.retire_shoe("Adidas Ultra", date(2024, 2, 1))
        
        # List them
        retired = service_with_temp_file.list_retired_shoes()
        assert len(retired) == 2
        assert "Nike Pegasus" in retired
        assert "Adidas Ultra" in retired
        assert retired["Nike Pegasus"].notes == "Worn out"
        assert retired["Adidas Ultra"].notes is None

    def test_directory_creation(self, temp_config_file):
        """Test that directory is created if it doesn't exist."""
        # Create a path with non-existent directory
        new_dir = temp_config_file.parent / "new_subdir"
        new_path = new_dir / "retired-shoes.json"
        
        service = RetirementService(config_path=new_path)
        service.retire_shoe("Test Shoe", date(2024, 1, 1))
        
        # Directory and file should be created
        assert new_dir.exists()
        assert new_path.exists()
        
        # Cleanup
        new_path.unlink()
        new_dir.rmdir()

    def test_atomic_file_operations(self, service_with_temp_file):
        """Test that file operations are atomic."""
        # This test verifies that a temporary file is created during save
        original_path = service_with_temp_file.config_path
        
        with patch('pathlib.Path.rename') as mock_rename:
            service_with_temp_file.retire_shoe("Test Shoe", date(2024, 1, 1))
            
            # Verify rename was called (atomic operation)
            mock_rename.assert_called_once()
            temp_path = mock_rename.call_args[0][0]
            assert str(temp_path).endswith('.tmp')

    def test_concurrent_access_simulation(self, temp_config_file):
        """Test behavior under simulated concurrent access."""
        # This test simulates concurrent reads and writes
        service1 = RetirementService(config_path=temp_config_file)
        service2 = RetirementService(config_path=temp_config_file)
        
        results = []
        errors = []
        
        def retire_shoes(service, shoe_name, thread_id):
            try:
                for i in range(5):
                    service.retire_shoe(
                        f"{shoe_name}_{i}",
                        date(2024, 1, i + 1),
                        f"Thread {thread_id}"
                    )
                    time.sleep(0.01)  # Small delay to increase chance of conflicts
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
        
        # Start concurrent operations
        thread1 = threading.Thread(target=retire_shoes, args=(service1, "Shoe", 1))
        thread2 = threading.Thread(target=retire_shoes, args=(service2, "Shoe", 2))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        assert len(results) == 2
        
        # Verify all shoes were saved
        final_service = RetirementService(config_path=temp_config_file)
        retired = final_service.list_retired_shoes()
        
        # Should have shoes from both threads
        shoe_count = len([k for k in retired.keys() if k.startswith("Shoe_")])
        assert shoe_count == 10  # 5 from each thread

    @patch('fcntl.flock')
    def test_file_locking_called(self, mock_flock, service_with_temp_file):
        """Test that file locking is properly called."""
        # Test read operation
        service_with_temp_file._load_retired_shoes()
        
        # For read, should acquire shared lock (LOCK_SH) and unlock
        assert mock_flock.call_count >= 2  # At least lock and unlock
        
        # Reset mock
        mock_flock.reset_mock()
        
        # Test write operation
        service_with_temp_file.retire_shoe("Test Shoe", date(2024, 1, 1))
        
        # For write, should acquire exclusive lock (LOCK_EX) and unlock
        assert mock_flock.call_count >= 2  # At least lock and unlock