import pytest
from datetime import date, datetime, timezone
import zoneinfo

from fitness.models import Run, LocalizedRun
from fitness.load.mmf import MmfActivity
from fitness.load.strava import StravaActivityWithGear


class TestRunModel:
    """Test the Run model."""

    def test_run_creation(self):
        """Test creating a Run instance."""
        run = Run(
            datetime_utc=datetime(2024, 1, 15, 10, 30, 0),
            type="Outdoor Run",
            distance=5.5,
            duration=1800,
            source="Strava",
            avg_heart_rate=150.0,
            shoes="Nike Pegasus"
        )
        
        assert run.datetime_utc == datetime(2024, 1, 15, 10, 30, 0)
        assert run.type == "Outdoor Run"
        assert run.distance == 5.5
        assert run.duration == 1800
        assert run.source == "Strava"
        assert run.avg_heart_rate == 150.0
        assert run.shoes == "Nike Pegasus"

    def test_run_optional_fields(self):
        """Test Run with optional fields as None."""
        run = Run(
            datetime_utc=datetime(2024, 1, 15, 10, 30, 0),
            type="Treadmill Run",
            distance=3.0,
            duration=1200,
            source="MapMyFitness",
            avg_heart_rate=None,
            shoes=None
        )
        
        assert run.avg_heart_rate is None
        assert run.shoes is None

    def test_model_dump_includes_date(self):
        """Test that model_dump includes backward-compatible date field."""
        run = Run(
            datetime_utc=datetime(2024, 1, 15, 10, 30, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava"
        )
        
        dumped = run.model_dump()
        assert 'date' in dumped
        assert dumped['date'] == date(2024, 1, 15)
        assert dumped['datetime_utc'] == datetime(2024, 1, 15, 10, 30, 0)

    def test_from_mmf_with_utc_date(self):
        """Test creating Run from MMF activity with UTC date."""
        mmf_activity = MmfActivity(
            activity_type="Run",
            distance=5.0,
            workout_time=1800,
            workout_date=date(2024, 1, 15),
            workout_date_utc=date(2024, 1, 15),
            avg_heart_rate=150.0,
            notes="Morning run with Nike shoes"
        )
        
        run = Run.from_mmf(mmf_activity)
        
        assert run.datetime_utc == datetime(2024, 1, 15, 0, 0, 0)
        assert run.type == "Outdoor Run"
        assert run.distance == 5.0
        assert run.duration == 1800
        assert run.avg_heart_rate == 150.0
        assert run.source == "MapMyFitness"
        assert run.shoes == "Nike"

    def test_from_mmf_without_utc_date(self):
        """Test creating Run from MMF activity without UTC date."""
        mmf_activity = MmfActivity(
            activity_type="Indoor Run / Jog",
            distance=3.0,
            workout_time=1200,
            workout_date=date(2024, 1, 15),
            workout_date_utc=None,  # No UTC date
            avg_heart_rate=145.0,
            notes=None
        )
        
        run = Run.from_mmf(mmf_activity)
        
        # Should fall back to workout_date
        assert run.datetime_utc == datetime(2024, 1, 15, 0, 0, 0)
        assert run.type == "Treadmill Run"
        assert run.shoes is None

    def test_from_strava(self):
        """Test creating Run from Strava activity."""
        strava_activity = StravaActivityWithGear(
            id=12345,
            name="Morning Run",
            distance=8046.72,  # 5 miles in meters
            moving_time=1800,
            elapsed_time=1850,
            total_elevation_gain=50.0,
            type="Run",
            sport_type="Run",
            start_date=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            start_date_local=datetime(2024, 1, 15, 5, 30, 0),
            timezone="(GMT-05:00) America/Chicago",
            start_latlng=[41.8781, -87.6298],
            end_latlng=[41.8781, -87.6298],
            average_speed=4.47,
            max_speed=5.0,
            average_heartrate=150.0,
            max_heartrate=165.0,
            elev_high=200.0,
            elev_low=180.0,
            upload_id=67890,
            external_id="garmin_12345",
            gear={"id": "g1234", "name": "Nike Pegasus 40", "distance": 100000}
        )
        
        run = Run.from_strava(strava_activity)
        
        # datetime_utc should be timezone-naive
        assert run.datetime_utc == datetime(2024, 1, 15, 10, 30, 0)
        assert run.datetime_utc.tzinfo is None
        assert run.type == "Outdoor Run"
        assert run.distance == pytest.approx(5.0, rel=0.01)
        assert run.duration == 1850  # Uses elapsed_time
        assert run.avg_heart_rate == 150.0
        assert run.shoes == "Nike Pegasus 40"
        assert run.source == "Strava"


class TestLocalizedRun:
    """Test the LocalizedRun model."""

    def test_localized_run_creation(self):
        """Test creating a LocalizedRun directly."""
        localized_run = LocalizedRun(
            datetime_utc=datetime(2024, 1, 15, 10, 30, 0),
            localized_datetime=datetime(2024, 1, 15, 5, 30, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava",
            avg_heart_rate=150.0,
            shoes="Nike"
        )
        
        assert localized_run.datetime_utc == datetime(2024, 1, 15, 10, 30, 0)
        assert localized_run.localized_datetime == datetime(2024, 1, 15, 5, 30, 0)
        assert localized_run.local_date == date(2024, 1, 15)

    def test_from_run_with_timezone(self):
        """Test converting a Run to LocalizedRun with timezone."""
        run = Run(
            datetime_utc=datetime(2024, 1, 15, 23, 30, 0),  # 11:30 PM UTC
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava",
            avg_heart_rate=150.0,
            shoes="Nike"
        )
        
        # Convert to Chicago time (UTC-6 in January)
        localized = LocalizedRun.from_run(run, "America/Chicago")
        
        assert localized.datetime_utc == datetime(2024, 1, 15, 23, 30, 0)
        assert localized.localized_datetime == datetime(2024, 1, 15, 17, 30, 0)  # 5:30 PM CST
        assert localized.local_date == date(2024, 1, 15)
        
        # All other fields should be preserved
        assert localized.type == "Outdoor Run"
        assert localized.distance == 5.0
        assert localized.duration == 1800
        assert localized.source == "Strava"
        assert localized.avg_heart_rate == 150.0
        assert localized.shoes == "Nike"

    def test_from_run_crosses_date_boundary(self):
        """Test LocalizedRun when timezone conversion crosses date boundary."""
        run = Run(
            datetime_utc=datetime(2024, 1, 16, 2, 0, 0),  # 2 AM UTC on Jan 16
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava"
        )
        
        # Convert to Chicago time (UTC-6) - should be Jan 15 at 8 PM
        chicago_run = LocalizedRun.from_run(run, "America/Chicago")
        assert chicago_run.localized_datetime == datetime(2024, 1, 15, 20, 0, 0)
        assert chicago_run.local_date == date(2024, 1, 15)
        
        # Convert to Tokyo time (UTC+9) - should be Jan 16 at 11 AM
        tokyo_run = LocalizedRun.from_run(run, "Asia/Tokyo")
        assert tokyo_run.localized_datetime == datetime(2024, 1, 16, 11, 0, 0)
        assert tokyo_run.local_date == date(2024, 1, 16)

    def test_from_run_daylight_saving(self):
        """Test LocalizedRun handles daylight saving time correctly."""
        # Summer date when Chicago is UTC-5 (CDT)
        summer_run = Run(
            datetime_utc=datetime(2024, 7, 15, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava"
        )
        
        chicago_summer = LocalizedRun.from_run(summer_run, "America/Chicago")
        assert chicago_summer.localized_datetime == datetime(2024, 7, 15, 5, 0, 0)  # 5 AM CDT
        
        # Winter date when Chicago is UTC-6 (CST)
        winter_run = Run(
            datetime_utc=datetime(2024, 1, 15, 10, 0, 0),
            type="Outdoor Run",
            distance=5.0,
            duration=1800,
            source="Strava"
        )
        
        chicago_winter = LocalizedRun.from_run(winter_run, "America/Chicago")
        assert chicago_winter.localized_datetime == datetime(2024, 1, 15, 4, 0, 0)  # 4 AM CST

    def test_run_type_mappings(self):
        """Test that run type mappings work correctly."""
        # Test MMF mappings
        assert Run.from_mmf(MmfActivity(
            activity_type="Run",
            distance=5.0,
            workout_time=1800,
            workout_date=date(2024, 1, 1),
            notes=""
        )).type == "Outdoor Run"
        
        assert Run.from_mmf(MmfActivity(
            activity_type="Indoor Run / Jog",
            distance=3.0,
            workout_time=1200,
            workout_date=date(2024, 1, 1),
            notes=""
        )).type == "Treadmill Run"
        
        # Test Strava mappings
        strava_outdoor = StravaActivityWithGear(
            id=1,
            name="Run",
            distance=5000,
            moving_time=1800,
            elapsed_time=1800,
            total_elevation_gain=0,
            type="Run",
            sport_type="Run",
            start_date=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            start_date_local=datetime(2024, 1, 1, 10, 0, 0),
            timezone="UTC",
            start_latlng=[],
            end_latlng=[],
            average_speed=2.78,
            max_speed=3.0,
            elev_high=0,
            elev_low=0,
            upload_id=1,
            external_id="1"
        )
        assert Run.from_strava(strava_outdoor).type == "Outdoor Run"
        
        strava_indoor = strava_outdoor.model_copy(update={"type": "Indoor Run"})
        assert Run.from_strava(strava_indoor).type == "Treadmill Run"
