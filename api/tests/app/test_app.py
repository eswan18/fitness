import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from fitness.app.app import app
from fitness.models import Run


client = TestClient(app)


@pytest.fixture
def mock_runs():
    """Create mock runs for testing."""
    return [
        Run(
            datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava",
            avg_heart_rate=150.0,
            shoes="Nike Pegasus",
        ),
        Run(
            datetime_utc=datetime(2024, 1, 2, 11, 0, 0),
            type="Treadmill Run",
            distance=3.0,
            duration=1200,
            source="MapMyFitness",
            avg_heart_rate=145.0,
            shoes="Adidas Ultra",
        ),
    ]


class TestAppEndpoints:
    """Test the main app endpoints."""

    def test_startup_event_handles_errors(self):
        """Test that startup event handles errors gracefully."""
        with patch('fitness.app.app.all_runs', side_effect=Exception("Connection error")):
            # Should not raise an exception
            from fitness.app.app import startup_event
            import asyncio
            asyncio.run(startup_event())

    @patch('fitness.app.dependencies.all_runs')
    def test_read_all_runs(self, mock_all_runs, mock_runs):
        """Test the /runs endpoint."""
        mock_all_runs.return_value = mock_runs
        
        response = client.get("/runs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["distance"] == 5.0
        assert data[1]["distance"] == 3.0

    @patch('fitness.app.dependencies.all_runs')
    def test_read_all_runs_with_date_filter(self, mock_all_runs, mock_runs):
        """Test the /runs endpoint with date filtering."""
        mock_all_runs.return_value = mock_runs
        
        response = client.get("/runs?start=2024-01-02&end=2024-01-02")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["distance"] == 3.0

    @patch('fitness.app.dependencies.all_runs')
    def test_read_all_runs_with_timezone(self, mock_all_runs, mock_runs):
        """Test the /runs endpoint with timezone parameter."""
        mock_all_runs.return_value = mock_runs
        
        response = client.get("/runs?user_timezone=America/Chicago")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch('fitness.app.dependencies.refresh_runs_data')
    def test_refresh_data_success(self, mock_refresh):
        """Test successful data refresh."""
        mock_refresh.return_value = [MagicMock(), MagicMock()]
        
        response = client.post("/refresh-data")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_runs"] == 2
        assert "refreshed_at" in data

    @patch('fitness.app.dependencies.refresh_runs_data')
    def test_refresh_data_error(self, mock_refresh):
        """Test data refresh with error handling."""
        mock_refresh.side_effect = Exception("Database connection failed")
        
        response = client.post("/refresh-data")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Database connection failed" in data["message"]
        assert data["total_runs"] == 0
        assert "refreshed_at" in data


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        response = client.options("/runs", headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
        assert response.headers["access-control-allow-credentials"] == "true"