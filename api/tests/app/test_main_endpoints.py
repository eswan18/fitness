"""Tests for main API endpoints."""

from datetime import date, datetime
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from fitness.app.app import app
from fitness.app.dependencies import all_runs, refresh_runs_data
from fitness.models import Run


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_runs():
    """Create sample runs for testing."""
    return [
        Run(
            datetime_utc=datetime(2024, 1, 15, 10, 0, 0),
            distance=5.0,
            duration=1800,  # 30 minutes
            type="Outdoor Run",
            source="Strava",
            shoes="Nike Air Zoom",
            avg_heart_rate=150,
        ),
        Run(
            datetime_utc=datetime(2024, 1, 10, 8, 0, 0),
            distance=3.0,
            duration=1200,  # 20 minutes
            type="Treadmill Run",
            source="MapMyFitness",
            shoes="Brooks Ghost",
            avg_heart_rate=165,
        ),
        Run(
            datetime_utc=datetime(2023, 12, 25, 7, 0, 0),
            distance=10.0,
            duration=3600,  # 60 minutes
            type="Outdoor Run",
            source="Strava",
            shoes="Nike Air Zoom",
            avg_heart_rate=140,
        ),
    ]


class TestRunsEndpoint:
    """Test the /runs endpoint."""

    def test_get_all_runs_default_params(self, client, sample_runs):
        """Test getting runs with default parameters."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs")
            
            assert response.status_code == 200
            runs = response.json()
            assert len(runs) == 3
            
            # Should be sorted by date desc by default (most recent first)
            # Check by datetime_utc since we don't have IDs
            assert runs[0]["datetime_utc"] == "2024-01-15T10:00:00"  # Most recent
            assert runs[1]["datetime_utc"] == "2024-01-10T08:00:00"
            assert runs[2]["datetime_utc"] == "2023-12-25T07:00:00"  # Oldest
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_with_date_filter(self, client, sample_runs):
        """Test filtering runs by date range."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?start=2024-01-01&end=2024-01-31")
            
            assert response.status_code == 200
            runs = response.json()
            assert len(runs) == 2  # Only runs from January 2024
            
            # Verify the correct runs are returned (from January 2024)
            datetimes = [run["datetime_utc"] for run in runs]
            assert "2024-01-15T10:00:00" in datetimes  # run1
            assert "2024-01-10T08:00:00" in datetimes  # run2
            assert "2023-12-25T07:00:00" not in datetimes  # run3 from 2023
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_sort_by_distance_asc(self, client, sample_runs):
        """Test sorting runs by distance ascending."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?sort_by=distance&sort_order=asc")
            
            assert response.status_code == 200
            runs = response.json()
            
            # Should be sorted by distance ascending
            assert runs[0]["distance"] == 3.0  # run2
            assert runs[1]["distance"] == 5.0  # run1
            assert runs[2]["distance"] == 10.0  # run3
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_sort_by_pace_desc(self, client, sample_runs):
        """Test sorting runs by pace descending."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?sort_by=pace&sort_order=desc")
            
            assert response.status_code == 200
            runs = response.json()
            
            # Pace calculation: (duration/60) / distance
            # run1: (1800/60) / 5.0 = 6.0 min/mile
            # run2: (1200/60) / 3.0 = 6.67 min/mile  
            # run3: (3600/60) / 10.0 = 6.0 min/mile
            # Desc order should be: run2 (slowest), then run1/run3
            assert runs[0]["datetime_utc"] == "2024-01-10T08:00:00"  # run2 - slowest pace
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_sort_by_heart_rate(self, client, sample_runs):
        """Test sorting runs by heart rate."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?sort_by=heart_rate&sort_order=desc")
            
            assert response.status_code == 200
            runs = response.json()
            
            # Should be sorted by heart rate descending
            assert runs[0]["avg_heart_rate"] == 165  # run2
            assert runs[1]["avg_heart_rate"] == 150  # run1
            assert runs[2]["avg_heart_rate"] == 140  # run3
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_sort_by_shoes(self, client, sample_runs):
        """Test sorting runs by shoes."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?sort_by=shoes&sort_order=asc")
            
            assert response.status_code == 200
            runs = response.json()
            
            # Should be sorted alphabetically by shoes
            assert runs[0]["shoes"] == "Brooks Ghost"  # run2
            assert runs[1]["shoes"] == "Nike Air Zoom"  # run1 or run3
            assert runs[2]["shoes"] == "Nike Air Zoom"
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_with_timezone(self, client, sample_runs):
        """Test getting runs with timezone conversion."""
        # Create runs that will definitely be in range
        today_runs = [
            Run(
                datetime_utc=datetime(2024, 6, 15, 10, 0, 0),
                distance=5.0,
                duration=1800,
                type="Outdoor Run",
                source="Strava",
                shoes="Nike Air Zoom",
                avg_heart_rate=150,
            )
        ]
        
        app.dependency_overrides[all_runs] = lambda: today_runs
        try:
            with patch("fitness.app.app.convert_runs_to_user_timezone") as mock_convert:
                # Mock the conversion to return localized runs
                from fitness.models import LocalizedRun
                localized_runs = [LocalizedRun.from_run(run, "America/New_York") for run in today_runs]
                mock_convert.return_value = localized_runs
                
                # Use default date range which should include our test run
                response = client.get("/runs?user_timezone=America/New_York")
                
                assert response.status_code == 200
                mock_convert.assert_called_once_with(today_runs, "America/New_York")
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_invalid_sort_field(self, client, sample_runs):
        """Test that invalid sort field returns 422 for invalid enum value."""
        app.dependency_overrides[all_runs] = lambda: sample_runs
        try:
            response = client.get("/runs?sort_by=invalid_field")
            
            # FastAPI validates the enum and returns 422 for invalid values
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_get_runs_with_zero_distance_pace_sorting(self, client):
        """Test pace sorting with zero distance runs."""
        zero_distance_run = Run(
            datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
            distance=0.0,
            duration=1800,
            type="Outdoor Run",
            source="Strava",
        )
        normal_run = Run(
            datetime_utc=datetime(2024, 1, 2, 10, 0, 0),
            distance=5.0,
            duration=1800,
            type="Outdoor Run",
            source="Strava",
        )
        
        app.dependency_overrides[all_runs] = lambda: [zero_distance_run, normal_run]
        try:
            response = client.get("/runs?sort_by=pace&sort_order=asc")
            
            assert response.status_code == 200
            runs = response.json()
            # Normal run should come first, zero distance should be last
            assert runs[0]["datetime_utc"] == "2024-01-02T10:00:00"  # normal_run
            assert runs[1]["datetime_utc"] == "2024-01-01T10:00:00"  # zero_run
        finally:
            app.dependency_overrides.clear()


class TestRefreshDataEndpoint:
    """Test the /refresh-data endpoint."""

    def test_refresh_data_success(self, client):
        """Test successful data refresh."""
        mock_runs = [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                distance=5.0,
                duration=1800,
                type="Outdoor Run",
                source="Strava",
            )
        ]
        
        with patch("fitness.app.app.refresh_runs_data") as mock_refresh:
            mock_refresh.return_value = mock_runs
            
            response = client.post("/refresh-data")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert data["message"] == "Data refreshed successfully"
            assert data["total_runs"] == 1
            assert "refreshed_at" in data
            
            # Verify refresh was called
            mock_refresh.assert_called_once()

    def test_refresh_data_empty_result(self, client):
        """Test refresh data with no runs returned."""
        with patch("fitness.app.app.refresh_runs_data") as mock_refresh:
            mock_refresh.return_value = []
            
            response = client.post("/refresh-data")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert data["total_runs"] == 0

    def test_refresh_data_datetime_format(self, client):
        """Test that refreshed_at is a valid ISO datetime."""
        with patch("fitness.app.app.refresh_runs_data") as mock_refresh:
            mock_refresh.return_value = []
            
            response = client.post("/refresh-data")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should be able to parse the datetime
            refreshed_at = datetime.fromisoformat(data["refreshed_at"])
            assert isinstance(refreshed_at, datetime)


class TestSortRunsFunction:
    """Test the sort_runs helper function directly."""

    def test_sort_runs_date_desc(self, sample_runs):
        """Test sorting by date descending."""
        from fitness.app.app import sort_runs
        
        sorted_runs = sort_runs(sample_runs, "date", "desc")
        
        # Check by datetime_utc since we don't have IDs
        assert sorted_runs[0].datetime_utc == datetime(2024, 1, 15, 10, 0, 0)  # Most recent
        assert sorted_runs[1].datetime_utc == datetime(2024, 1, 10, 8, 0, 0)
        assert sorted_runs[2].datetime_utc == datetime(2023, 12, 25, 7, 0, 0)  # Oldest

    def test_sort_runs_distance_asc(self, sample_runs):
        """Test sorting by distance ascending."""
        from fitness.app.app import sort_runs
        
        sorted_runs = sort_runs(sample_runs, "distance", "asc")
        
        assert sorted_runs[0].distance == 3.0  # run2
        assert sorted_runs[1].distance == 5.0  # run1
        assert sorted_runs[2].distance == 10.0  # run3

    def test_sort_runs_duration_desc(self, sample_runs):
        """Test sorting by duration descending."""
        from fitness.app.app import sort_runs
        
        sorted_runs = sort_runs(sample_runs, "duration", "desc")
        
        assert sorted_runs[0].duration == 3600  # run3
        assert sorted_runs[1].duration == 1800  # run1
        assert sorted_runs[2].duration == 1200  # run2

    def test_sort_runs_with_none_heart_rate(self):
        """Test sorting with None heart rate values."""
        from fitness.app.app import sort_runs
        
        runs_with_none = [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                distance=5.0,
                duration=1800,
                type="Outdoor Run",
                source="Strava",
                avg_heart_rate=None,
            ),
            Run(
                datetime_utc=datetime(2024, 1, 2, 10, 0, 0),
                distance=5.0,
                duration=1800,
                type="Outdoor Run",
                source="Strava",
                avg_heart_rate=150,
            ),
        ]
        
        sorted_runs = sort_runs(runs_with_none, "heart_rate", "asc")
        
        # None values should be treated as 0 and come first
        assert sorted_runs[0].avg_heart_rate is None
        assert sorted_runs[1].avg_heart_rate == 150

    def test_sort_runs_error_handling(self, sample_runs):
        """Test that sorting errors are handled gracefully."""
        from fitness.app.app import sort_runs
        
        # This should not raise an exception and return unsorted runs
        result = sort_runs(sample_runs, "invalid_field", "asc")
        
        # Should return the runs (potentially unsorted due to fallback)
        assert len(result) == len(sample_runs) 