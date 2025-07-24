import pytest
from datetime import datetime, date
import math

from fitness.agg.training_load import trimp, training_stress_balance, trimp_by_day
from fitness.models import Run, Sex


class TestTrimpCalculation:
    """Test TRIMP calculation function."""

    @pytest.fixture
    def sample_run(self):
        """Create a sample run for testing."""
        return Run(
            datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,  # 30 minutes
            source="Strava",
            avg_heart_rate=150.0,
        )

    def test_trimp_male(self, sample_run):
        """Test TRIMP calculation for male."""
        result = trimp(sample_run, max_hr=190.0, resting_hr=50.0, sex="M")
        
        # Manual calculation
        hr_relative = (150.0 - 50.0) / (190.0 - 50.0)  # 0.7143
        y = 0.64 * math.exp(1.92 * hr_relative)  # ≈ 2.52
        expected = 30 * hr_relative * y  # ≈ 53.96
        
        assert abs(result - expected) < 0.1

    def test_trimp_female(self, sample_run):
        """Test TRIMP calculation for female."""
        result = trimp(sample_run, max_hr=190.0, resting_hr=50.0, sex="F")
        
        # Manual calculation
        hr_relative = (150.0 - 50.0) / (190.0 - 50.0)  # 0.7143
        y = 0.86 * math.exp(1.67 * hr_relative)  # ≈ 2.82
        expected = 30 * hr_relative * y  # ≈ 60.43
        
        assert abs(result - expected) < 0.1

    def test_trimp_no_heart_rate(self):
        """Test TRIMP calculation with missing heart rate."""
        run = Run(
            datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava",
            avg_heart_rate=None,
        )
        
        with pytest.raises(ValueError, match="Run must have an average heart rate"):
            trimp(run, max_hr=190.0, resting_hr=50.0, sex="M")

    def test_trimp_invalid_heart_rates(self, sample_run):
        """Test TRIMP calculation with invalid heart rate values."""
        # Max HR <= Resting HR
        with pytest.raises(ValueError, match="Max heart rate.*must be greater than resting heart rate"):
            trimp(sample_run, max_hr=50.0, resting_hr=50.0, sex="M")
        
        # Negative heart rates
        with pytest.raises(ValueError, match="Heart rate values must be non-negative"):
            trimp(sample_run, max_hr=-190.0, resting_hr=50.0, sex="M")
        
        with pytest.raises(ValueError, match="Heart rate values must be non-negative"):
            trimp(sample_run, max_hr=190.0, resting_hr=-50.0, sex="M")

    def test_trimp_hr_relative_clamping(self):
        """Test that HR relative is clamped to [0, 1]."""
        # Test with avg HR above max HR
        run = Run(
            datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,  # 30 minutes
            source="Strava",
            avg_heart_rate=200.0,  # Above max
        )
        
        result = trimp(run, max_hr=190.0, resting_hr=50.0, sex="M")
        
        # HR relative should be clamped to 1.0
        y = 0.64 * math.exp(1.92 * 1.0)
        expected = 30 * 1.0 * y
        
        assert abs(result - expected) < 0.1
        
        # Test with avg HR below resting HR
        run.avg_heart_rate = 40.0  # Below resting
        
        result = trimp(run, max_hr=190.0, resting_hr=50.0, sex="M")
        
        # HR relative should be clamped to 0.0
        y = 0.64 * math.exp(1.92 * 0.0)
        expected = 30 * 0.0 * y
        
        assert result == 0.0


class TestTrainingStressBalance:
    """Test training stress balance calculations."""

    @pytest.fixture
    def sample_runs_with_hr(self):
        """Create sample runs with heart rate data."""
        return [
            Run(
                datetime_utc=datetime(2024, 1, i, 10, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,  # 30 minutes
                source="Strava",
                avg_heart_rate=140.0 + i * 2,  # Varying heart rates
            )
            for i in range(1, 8)
        ]

    def test_training_stress_balance(self, sample_runs_with_hr):
        """Test TSB calculation."""
        result = training_stress_balance(
            runs=sample_runs_with_hr,
            max_hr=190.0,
            resting_hr=50.0,
            sex="M",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )
        
        assert len(result) == 7
        
        # Check that each day has the expected fields
        for day_load in result:
            assert hasattr(day_load, 'date')
            assert hasattr(day_load, 'trimp')
            assert hasattr(day_load, 'atl')
            assert hasattr(day_load, 'ctl')
            assert hasattr(day_load, 'tsb')
            
            # TSB = CTL - ATL
            assert abs(day_load.tsb - (day_load.ctl - day_load.atl)) < 0.01

    def test_training_stress_balance_empty_runs(self):
        """Test TSB calculation with no runs."""
        result = training_stress_balance(
            runs=[],
            max_hr=190.0,
            resting_hr=50.0,
            sex="M",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )
        
        assert len(result) == 7
        
        # All values should be zero
        for day_load in result:
            assert day_load.trimp == 0.0
            assert day_load.atl == 0.0
            assert day_load.ctl == 0.0
            assert day_load.tsb == 0.0

    def test_training_stress_balance_filters_no_hr(self):
        """Test that TSB filters out runs without heart rate."""
        runs = [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
                avg_heart_rate=150.0,
            ),
            Run(
                datetime_utc=datetime(2024, 1, 2, 10, 0, 0),
                type="Outdoor Run",
                distance=3.0,
                duration=1200,
                source="Strava",
                avg_heart_rate=None,  # No HR
            ),
        ]
        
        result = training_stress_balance(
            runs=runs,
            max_hr=190.0,
            resting_hr=50.0,
            sex="M",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
        )
        
        assert len(result) == 2
        assert result[0].trimp > 0  # First day has TRIMP
        assert result[1].trimp == 0  # Second day has no TRIMP (no HR)


class TestTRIMPByDay:
    """Test TRIMP by day aggregation."""

    @pytest.fixture
    def sample_runs_multiple_per_day(self):
        """Create sample runs with multiple runs per day."""
        return [
            Run(
                datetime_utc=datetime(2024, 1, 1, 10, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
                avg_heart_rate=150.0,
            ),
            Run(
                datetime_utc=datetime(2024, 1, 1, 18, 0, 0),
                type="Outdoor Run",
                distance=3.0,
                duration=1200,
                source="Strava",
                avg_heart_rate=140.0,
            ),
            Run(
                datetime_utc=datetime(2024, 1, 2, 10, 0, 0),
                type="Outdoor Run",
                distance=7.0,
                duration=2400,
                source="Strava",
                avg_heart_rate=155.0,
            ),
        ]

    def test_trimp_by_day_aggregation(self, sample_runs_multiple_per_day):
        """Test that TRIMP values are aggregated correctly by day."""
        result = trimp_by_day(
            runs=sample_runs_multiple_per_day,
            start=date(2024, 1, 1),
            end=date(2024, 1, 2),
            max_hr=190.0,
            resting_hr=50.0,
            sex="M",
        )
        
        assert len(result) == 2
        
        # First day should have combined TRIMP from both runs
        day1_trimp = result[0].trimp
        
        # Calculate expected TRIMP for each run
        run1_trimp = trimp(sample_runs_multiple_per_day[0], 190.0, 50.0, "M")
        run2_trimp = trimp(sample_runs_multiple_per_day[1], 190.0, 50.0, "M")
        
        assert abs(day1_trimp - (run1_trimp + run2_trimp)) < 0.1
        
        # Second day should have TRIMP from single run
        day2_trimp = result[1].trimp
        run3_trimp = trimp(sample_runs_multiple_per_day[2], 190.0, 50.0, "M")
        
        assert abs(day2_trimp - run3_trimp) < 0.1
