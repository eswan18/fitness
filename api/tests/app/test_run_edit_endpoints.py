"""
Tests for run editing API endpoints.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from fitness.app.app import app
from fitness.models import Run
from fitness.db.runs_history import RunHistoryRecord

client = TestClient(app)


@pytest.fixture
def sample_run():
    """Create a sample run for testing."""
    return Run(
        id="test_run_123",
        datetime_utc=datetime(2024, 1, 15, 10, 0, 0),
        type="Outdoor Run",
        distance=5.0,
        duration=1800.0,
        source="Strava",
        avg_heart_rate=150.0,
        shoe_id="nike_pegasus_38"
    )


@pytest.fixture
def sample_history_record():
    """Create a sample history record for testing."""
    return RunHistoryRecord(
        history_id=1,
        run_id="test_run_123",
        version_number=1,
        change_type="original",
        datetime_utc=datetime(2024, 1, 15, 10, 0, 0),
        type="Outdoor Run",
        distance=5.0,
        duration=1800.0,
        source="Strava",
        avg_heart_rate=150.0,
        shoe_id="nike_pegasus_38",
        changed_at=datetime(2024, 1, 15, 12, 0, 0),
        changed_by="system",
        change_reason="Initial import"
    )


class TestUpdateRunEndpoint:
    """Test the PATCH /runs/{run_id} endpoint."""

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.update_run_with_history')
    def test_update_run_success(self, mock_update, mock_get_run, sample_run):
        """Test successful run update."""
        # Setup mocks
        mock_get_run.return_value = sample_run
        mock_update.return_value = None
        
        # Updated run with new values
        updated_run = Run(
            id="test_run_123",
            datetime_utc=datetime(2024, 1, 15, 10, 0, 0),
            type="Outdoor Run",
            distance=5.5,  # Updated
            duration=1800.0,
            source="Strava",
            avg_heart_rate=155.0,  # Updated
            shoe_id="nike_pegasus_38"
        )
        
        # Mock the second get_run_by_id call for returning updated run
        mock_get_run.side_effect = [sample_run, updated_run]

        # Request data
        update_data = {
            "distance": 5.5,
            "avg_heart_rate": 155.0,
            "datetime_utc": "2024-01-15T10:05:00",  # Updated start time
            "changed_by": "user123",
            "change_reason": "Corrected GPS data and start time"
        }

        # Execute
        response = client.patch("/runs/test_run_123", json=update_data)

        # Verify
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["updated_by"] == "user123"
        assert "distance" in result["updated_fields"]
        assert "avg_heart_rate" in result["updated_fields"]
        
        # Verify the update was called correctly  
        mock_update.assert_called_once_with(
            run_id="test_run_123",
            updates={"distance": 5.5, "avg_heart_rate": 155.0, "datetime_utc": datetime(2024, 1, 15, 10, 5, 0)},
            changed_by="user123",
            change_reason="Corrected GPS data and start time"
        )

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_update_run_not_found(self, mock_get_run):
        """Test update of non-existent run."""
        mock_get_run.return_value = None

        update_data = {
            "distance": 5.5,
            "changed_by": "user123"
        }

        response = client.patch("/runs/nonexistent_run", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_update_run_no_fields(self, mock_get_run, sample_run):
        """Test update with no valid fields provided."""
        mock_get_run.return_value = sample_run
        
        update_data = {
            "changed_by": "user123",
            "change_reason": "Testing"
        }

        response = client.patch("/runs/test_run_123", json=update_data)

        assert response.status_code == 400
        assert "No valid fields provided" in response.json()["detail"]

    def test_update_run_missing_changed_by(self):
        """Test update without required changed_by field."""
        update_data = {
            "distance": 5.5
        }

        response = client.patch("/runs/test_run_123", json=update_data)

        assert response.status_code == 422  # Validation error

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_update_run_invalid_field(self, mock_get_run, sample_run):
        """Test update with invalid field (ignored by Pydantic, no valid fields remain)."""
        mock_get_run.return_value = sample_run

        update_data = {
            "source": "MapMyFitness",  # This field is not in RunUpdateRequest, so ignored
            "changed_by": "user123"
        }

        response = client.patch("/runs/test_run_123", json=update_data)

        assert response.status_code == 400
        assert "No valid fields provided" in response.json()["detail"]


class TestGetRunHistoryEndpoint:
    """Test the GET /runs/{run_id}/history endpoint."""

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_history')
    def test_get_run_history_success(self, mock_get_history, mock_get_run, sample_run, sample_history_record):
        """Test successful history retrieval."""
        mock_get_run.return_value = sample_run
        mock_get_history.return_value = [sample_history_record]

        response = client.get("/runs/test_run_123/history")

        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["run_id"] == "test_run_123"
        assert result[0]["version_number"] == 1
        assert result[0]["change_type"] == "original"

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_get_run_history_run_not_found(self, mock_get_run):
        """Test history retrieval for non-existent run."""
        mock_get_run.return_value = None

        response = client.get("/runs/nonexistent_run/history")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_history')
    def test_get_run_history_with_limit(self, mock_get_history, mock_get_run, sample_run):
        """Test history retrieval with limit parameter."""
        mock_get_run.return_value = sample_run
        mock_get_history.return_value = []

        response = client.get("/runs/test_run_123/history?limit=10")

        assert response.status_code == 200
        mock_get_history.assert_called_once_with("test_run_123", limit=10)


class TestGetRunVersionEndpoint:
    """Test the GET /runs/{run_id}/history/{version_number} endpoint."""

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_version')
    def test_get_run_version_success(self, mock_get_version, mock_get_run, sample_run, sample_history_record):
        """Test successful version retrieval."""
        mock_get_run.return_value = sample_run
        mock_get_version.return_value = sample_history_record

        response = client.get("/runs/test_run_123/history/1")

        assert response.status_code == 200
        result = response.json()
        assert result["run_id"] == "test_run_123"
        assert result["version_number"] == 1

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_get_run_version_run_not_found(self, mock_get_run):
        """Test version retrieval for non-existent run."""
        mock_get_run.return_value = None

        response = client.get("/runs/nonexistent_run/history/1")

        assert response.status_code == 404

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_version')
    def test_get_run_version_not_found(self, mock_get_version, mock_get_run, sample_run):
        """Test retrieval of non-existent version."""
        mock_get_run.return_value = sample_run
        mock_get_version.return_value = None

        response = client.get("/runs/test_run_123/history/99")

        assert response.status_code == 404
        assert "Version 99 not found" in response.json()["detail"]


class TestBackfillEndpoint:
    """Test the POST /runs/history/backfill endpoint."""

    @patch('fitness.app.run_edit_routes.create_original_history_entries')
    def test_backfill_success(self, mock_backfill):
        """Test successful backfill operation."""
        mock_backfill.return_value = 150

        response = client.post("/runs/history/backfill")

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["records_processed"] == 150
        
        mock_backfill.assert_called_once_with(1000)  # default batch size

    @patch('fitness.app.run_edit_routes.create_original_history_entries')
    def test_backfill_with_custom_batch_size(self, mock_backfill):
        """Test backfill with custom batch size."""
        mock_backfill.return_value = 50

        response = client.post("/runs/history/backfill?batch_size=500")

        assert response.status_code == 200
        mock_backfill.assert_called_once_with(500)

    def test_backfill_invalid_batch_size(self):
        """Test backfill with invalid batch size."""
        response = client.post("/runs/history/backfill?batch_size=0")
        assert response.status_code == 400

        response = client.post("/runs/history/backfill?batch_size=6000")
        assert response.status_code == 400

    @patch('fitness.app.run_edit_routes.create_original_history_entries')
    def test_backfill_no_records(self, mock_backfill):
        """Test backfill when no records need processing."""
        mock_backfill.return_value = 0

        response = client.post("/runs/history/backfill")

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "no_action_needed"


class TestRestoreRunEndpoint:
    """Test the POST /runs/{run_id}/restore/{version_number} endpoint."""

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_version')
    @patch('fitness.app.run_edit_routes.update_run_with_history')
    def test_restore_run_success(self, mock_update, mock_get_version, mock_get_run, 
                                sample_run, sample_history_record):
        """Test successful run restoration."""
        mock_get_run.return_value = sample_run
        mock_get_version.return_value = sample_history_record
        mock_update.return_value = None
        
        # Mock the second get_run_by_id call for returning restored run
        mock_get_run.side_effect = [sample_run, sample_run]

        response = client.post("/runs/test_run_123/restore/1?restored_by=user123")

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["restored_from_version"] == 1
        assert result["restored_by"] == "user123"

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    def test_restore_run_not_found(self, mock_get_run):
        """Test restoration of non-existent run."""
        mock_get_run.return_value = None

        response = client.post("/runs/nonexistent_run/restore/1?restored_by=user123")

        assert response.status_code == 404

    @patch('fitness.app.run_edit_routes.get_run_by_id')
    @patch('fitness.app.run_edit_routes.get_run_version')
    def test_restore_run_version_not_found(self, mock_get_version, mock_get_run, sample_run):
        """Test restoration to non-existent version."""
        mock_get_run.return_value = sample_run
        mock_get_version.return_value = None

        response = client.post("/runs/test_run_123/restore/99?restored_by=user123")

        assert response.status_code == 404
        assert "Version 99 not found" in response.json()["detail"]