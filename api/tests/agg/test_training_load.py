import pytest
from datetime import date
from fitness.agg.training_load import trimp, trimp_by_day
from tests._factories.run import RunFactory


class TestTrimp:
    """Tests for the trimp() function."""

    def test_trimp_calculation_male(self):
        """Test TRIMP calculation for male runner."""
        run = RunFactory().make({
            "date": date(2024, 1, 1),
            "duration": 2400,  # 40 minutes
            "avg_heart_rate": 150,
        })
        
        result = trimp(run, max_hr=190, resting_hr=50, sex="M")
        
        # Expected calculation:
        # hr_relative = (150 - 50) / (190 - 50) = 100/140 ≈ 0.714
        # y = 0.64 * exp(1.92 * 0.714) ≈ 0.64 * exp(1.371) ≈ 0.64 * 3.94 ≈ 2.52
        # duration_minutes = 2400 / 60 = 40
        # trimp = 40 * 0.714 * 2.52 ≈ 72.1
        assert result == pytest.approx(72.1, abs=1.0)

    def test_trimp_calculation_female(self):
        """Test TRIMP calculation for female runner."""
        run = RunFactory().make({
            "date": date(2024, 1, 1),
            "duration": 2400,  # 40 minutes
            "avg_heart_rate": 150,
        })
        
        result = trimp(run, max_hr=190, resting_hr=50, sex="F")
        
        # Expected calculation:
        # hr_relative = (150 - 50) / (190 - 50) = 100/140 ≈ 0.714
        # y = 0.86 * exp(1.67 * 0.714) ≈ 0.86 * exp(1.192) ≈ 0.86 * 3.29 ≈ 2.83
        # duration_minutes = 2400 / 60 = 40
        # trimp = 40 * 0.714 * 2.83 ≈ 80.9
        assert result == pytest.approx(80.9, abs=1.0)

    def test_trimp_no_heart_rate(self):
        """Test that TRIMP calculation raises error when no heart rate."""
        run = RunFactory().make({
            "date": date(2024, 1, 1),
            "duration": 2400,
            "avg_heart_rate": None,
        })
        
        with pytest.raises(ValueError, match="Run must have an average heart rate"):
            trimp(run, max_hr=190, resting_hr=50, sex="M")

    def test_trimp_hr_clamping(self):
        """Test that heart rate relative is clamped to [0, 1] range."""
        # Test with heart rate above max_hr
        run_high = RunFactory().make({
            "date": date(2024, 1, 1),
            "duration": 3600,  # 60 minutes
            "avg_heart_rate": 200,  # Above max_hr of 190
        })
        
        result_high = trimp(run_high, max_hr=190, resting_hr=50, sex="M")
        
        # Should be clamped to hr_relative = 1.0
        # y = 0.64 * exp(1.92 * 1.0) ≈ 0.64 * 6.82 ≈ 4.36
        # trimp = 60 * 1.0 * 4.36 ≈ 261.8
        assert result_high == pytest.approx(261.8, abs=5.0)

        # Test with heart rate below resting_hr
        run_low = RunFactory().make({
            "date": date(2024, 1, 1),
            "duration": 3600,  # 60 minutes
            "avg_heart_rate": 40,  # Below resting_hr of 50
        })
        
        result_low = trimp(run_low, max_hr=190, resting_hr=50, sex="M")
        
        # Should be clamped to hr_relative = 0.0
        # y = 0.64 * exp(1.92 * 0.0) = 0.64 * 1 = 0.64
        # trimp = 60 * 0.0 * 0.64 = 0
        assert result_low == 0.0


class TestTrimpByDay:
    """Tests for the trimp_by_day() function."""

    def test_single_run_day(self):
        """Test TRIMP calculation for a single run on one day."""
        runs = [
            RunFactory().make({
                "date": date(2024, 1, 15),
                "duration": 2400,  # 40 minutes
                "avg_heart_rate": 150,
            })
        ]
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 15),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 1
        assert result[0].date == date(2024, 1, 15)
        assert result[0].trimp == pytest.approx(72.1, abs=1.0)

    def test_multiple_runs_same_day(self):
        """Test TRIMP calculation for multiple runs on the same day."""
        runs = [
            RunFactory().make({
                "date": date(2024, 1, 15),
                "distance": 3.0,
                "duration": 1800,  # 30 minutes
                "avg_heart_rate": 140,
            }),
            RunFactory().make({
                "date": date(2024, 1, 15),
                "distance": 2.0,
                "duration": 1200,  # 20 minutes
                "avg_heart_rate": 160,
            })
        ]
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 15),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 1
        assert result[0].date == date(2024, 1, 15)
        # Should be sum of both runs' TRIMP values
        assert result[0].trimp > 0

    def test_multiple_days_with_gaps(self):
        """Test TRIMP calculation across multiple days including days with no runs."""
        runs = [
            RunFactory().make({
                "date": date(2024, 1, 15),
                "duration": 2400,
                "avg_heart_rate": 150,
            }),
            RunFactory().make({
                "date": date(2024, 1, 17),  # Skip Jan 16
                "distance": 3.0,
                "duration": 1800,
                "avg_heart_rate": 140,
            })
        ]
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 17),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 3  # 3 days total
        assert result[0].date == date(2024, 1, 15)
        assert result[0].trimp > 0  # Has a run
        assert result[1].date == date(2024, 1, 16)
        assert result[1].trimp == 0.0  # No runs
        assert result[2].date == date(2024, 1, 17)
        assert result[2].trimp > 0  # Has a run

    def test_runs_without_heart_rate_excluded(self):
        """Test that runs without heart rate data are excluded from TRIMP calculation."""
        runs = [
            RunFactory().make({
                "date": date(2024, 1, 15),
                "duration": 2400,
                "avg_heart_rate": 150,  # Has heart rate
            }),
            RunFactory().make({
                "date": date(2024, 1, 15),
                "distance": 3.0,
                "duration": 1800,
                "avg_heart_rate": None,  # No heart rate
            })
        ]
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 15),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 1
        assert result[0].date == date(2024, 1, 15)
        # Should only include TRIMP from the run with heart rate data
        expected_trimp = trimp(runs[0], max_hr=190, resting_hr=50, sex="M")
        assert result[0].trimp == pytest.approx(expected_trimp, abs=0.1)

    def test_no_runs_in_range(self):
        """Test TRIMP calculation when no runs exist in the date range."""
        runs = []
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 17),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 3  # 3 days in range
        for day_trimp in result:
            assert day_trimp.trimp == 0.0

    def test_runs_outside_date_range_excluded(self):
        """Test that runs outside the specified date range are excluded."""
        runs = [
            RunFactory().make({
                "date": date(2024, 1, 14),  # Before range
                "duration": 2400,
                "avg_heart_rate": 150,
            }),
            RunFactory().make({
                "date": date(2024, 1, 15),  # In range
                "distance": 3.0,
                "duration": 1800,
                "avg_heart_rate": 140,
            }),
            RunFactory().make({
                "date": date(2024, 1, 18),  # After range
                "distance": 4.0,
                "duration": 2000,
                "avg_heart_rate": 145,
            })
        ]
        
        result = trimp_by_day(
            runs=runs,
            start=date(2024, 1, 15),
            end=date(2024, 1, 17),
            max_hr=190,
            resting_hr=50,
            sex="M"
        )
        
        assert len(result) == 3  # 3 days in range
        assert result[0].date == date(2024, 1, 15)
        assert result[0].trimp > 0  # Only the run on Jan 15
        assert result[1].trimp == 0.0  # No runs on Jan 16
        assert result[2].trimp == 0.0  # No runs on Jan 17