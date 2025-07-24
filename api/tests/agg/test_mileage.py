import pytest
from datetime import date, datetime, timedelta

from fitness.agg.mileage import (
    total_mileage,
    avg_miles_per_day,
    miles_by_day,
    rolling_sum,
)
from fitness.models import Run


class TestMileageAggregations:
    """Test mileage aggregation functions."""

    @pytest.fixture
    def sample_runs(self):
        """Create sample runs for testing."""
        return [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
            ),
            Run(
                datetime_utc=datetime(2024, 1, 2, 11, 0, 0),
                type="Outdoor Run",
                distance=3.0,
                duration=1200,
                source="Strava",
            ),
            Run(
                datetime_utc=datetime(2024, 1, 3, 9, 0, 0),
                type="Outdoor Run",
                distance=7.0,
                duration=2400,
                source="Strava",
            ),
        ]

    def test_total_mileage(self, sample_runs):
        """Test total mileage calculation."""
        result = total_mileage(sample_runs, date(2024, 1, 1), date(2024, 1, 3))
        assert result == 15.0

    def test_total_mileage_partial_range(self, sample_runs):
        """Test total mileage with partial date range."""
        result = total_mileage(sample_runs, date(2024, 1, 2), date(2024, 1, 2))
        assert result == 3.0

    def test_total_mileage_empty_range(self, sample_runs):
        """Test total mileage with no runs in range."""
        result = total_mileage(sample_runs, date(2024, 2, 1), date(2024, 2, 28))
        assert result == 0.0

    def test_avg_miles_per_day(self, sample_runs):
        """Test average miles per day calculation."""
        result = avg_miles_per_day(sample_runs, date(2024, 1, 1), date(2024, 1, 3))
        assert result == 5.0  # 15 miles / 3 days

    def test_avg_miles_per_day_single_day(self, sample_runs):
        """Test average miles per day for a single day."""
        result = avg_miles_per_day(sample_runs, date(2024, 1, 1), date(2024, 1, 1))
        assert result == 5.0  # 5 miles / 1 day

    def test_avg_miles_per_day_invalid_range(self, sample_runs):
        """Test average miles per day with end before start."""
        result = avg_miles_per_day(sample_runs, date(2024, 1, 3), date(2024, 1, 1))
        assert result == 0.0

    def test_miles_by_day(self, sample_runs):
        """Test miles by day calculation."""
        result = miles_by_day(sample_runs, date(2024, 1, 1), date(2024, 1, 3))
        assert len(result) == 3
        assert result[0] == (date(2024, 1, 1), 5.0)
        assert result[1] == (date(2024, 1, 2), 3.0)
        assert result[2] == (date(2024, 1, 3), 7.0)

    def test_miles_by_day_with_gaps(self):
        """Test miles by day with gaps in runs."""
        runs = [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
            ),
            Run(
                datetime_utc=datetime(2024, 1, 3, 10, 0, 0),
                type="Outdoor Run",
                distance=3.0,
                duration=1200,
                source="Strava",
            ),
        ]
        result = miles_by_day(runs, date(2024, 1, 1), date(2024, 1, 3))
        assert len(result) == 3
        assert result[0] == (date(2024, 1, 1), 5.0)
        assert result[1] == (date(2024, 1, 2), 0.0)
        assert result[2] == (date(2024, 1, 3), 3.0)

    def test_rolling_sum_window_1(self, sample_runs):
        """Test rolling sum with window of 1 (same as miles_by_day)."""
        result = rolling_sum(sample_runs, date(2024, 1, 1), date(2024, 1, 3), window=1)
        assert len(result) == 3
        assert result[0] == (date(2024, 1, 1), 5.0)
        assert result[1] == (date(2024, 1, 2), 3.0)
        assert result[2] == (date(2024, 1, 3), 7.0)

    def test_rolling_sum_window_2(self, sample_runs):
        """Test rolling sum with window of 2."""
        result = rolling_sum(sample_runs, date(2024, 1, 1), date(2024, 1, 3), window=2)
        assert len(result) == 3
        assert result[0] == (date(2024, 1, 1), 5.0)  # Only day 1
        assert result[1] == (date(2024, 1, 2), 8.0)  # Days 1 + 2
        assert result[2] == (date(2024, 1, 3), 10.0)  # Days 2 + 3

    def test_rolling_sum_window_larger_than_range(self, sample_runs):
        """Test rolling sum with window larger than date range."""
        result = rolling_sum(sample_runs, date(2024, 1, 2), date(2024, 1, 3), window=5)
        assert len(result) == 2
        assert result[0] == (date(2024, 1, 2), 8.0)  # Days 1 + 2
        assert result[1] == (date(2024, 1, 3), 15.0)  # Days 1 + 2 + 3

    def test_rolling_sum_floating_point_precision(self):
        """Test that rolling sum handles floating point precision correctly."""
        runs = [
            Run(
                datetime_utc=datetime(2024, 1, i, 10, 0, 0),
                type="Outdoor Run",
                distance=0.1111111,
                duration=600,
                source="Strava",
            )
            for i in range(1, 10)
        ]
        result = rolling_sum(runs, date(2024, 1, 5), date(2024, 1, 5), window=5)
        assert len(result) == 1
        # Should be rounded to 4 decimal places
        assert result[0][1] == 0.5556  # 5 * 0.1111111 ≈ 0.5556

    def test_mileage_with_timezone(self, sample_runs):
        """Test mileage calculations with timezone conversion."""
        # Add a run that crosses midnight UTC
        runs = sample_runs + [
            Run(
                datetime_utc=datetime(2024, 1, 3, 23, 30, 0),  # 11:30 PM UTC
                type="Outdoor Run",
                distance=2.0,
                duration=900,
                source="Strava",
            )
        ]
        
        # In Chicago time (UTC-6), this run would be on Jan 3 at 5:30 PM
        result = total_mileage(runs, date(2024, 1, 3), date(2024, 1, 3), "America/Chicago")
        assert result == 9.0  # 7.0 + 2.0

        # In Tokyo time (UTC+9), this run would be on Jan 4 at 8:30 AM
        result = total_mileage(runs, date(2024, 1, 4), date(2024, 1, 4), "Asia/Tokyo")
        assert result == 2.0  # Only the late run
