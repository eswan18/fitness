from datetime import datetime, timezone

import pytest

from fitness.models import Run
from tests._factories import StravaActivityWithGearFactory, MmfActivityFactory


def test_run_from_strava(
    strava_activity_with_gear_factory: StravaActivityWithGearFactory,
):
    activity = strava_activity_with_gear_factory.make(
        update={
            "start_date": datetime(2024, 11, 4, tzinfo=timezone.utc),
            "type": "Run",
            "distance": 8046.72,  # 5 miles in meters
            "moving_time": 1800,
            "elapsed_time": 1800,
            "average_heartrate": 150.0,
        }
    )
    run = Run.from_strava(activity)
    assert run.datetime_utc == datetime(2024, 11, 4)
    assert run.type == "Outdoor Run"
    assert run.distance == pytest.approx(5)
    assert run.duration == 1800
    assert run.avg_heart_rate == 150.0
    assert run.shoes == activity.gear.nickname
    assert run.source == "Strava"


def test_run_from_mmf_activity(mmf_activity_factory: MmfActivityFactory):
    activity = mmf_activity_factory.make(
        update={
            "workout_date": datetime(2024, 11, 5, tzinfo=timezone.utc),
            "activity_type": "Run",
            "distance": 6,  # Unlike strava, MMF uses miles
            "workout_time": 1800,
            "avg_heart_rate": 154.0,
            "notes": "Shoes: Nike Air Zoom",
        }
    )
    run = Run.from_mmf(activity)
    assert run.datetime_utc == datetime(2024, 11, 5, 0, 0, 0)
    assert run.type == "Outdoor Run"
    assert run.distance == 6
    assert run.duration == 1800
    assert run.avg_heart_rate == 154.0
    assert run.shoes == "Nike Air Zoom"
    assert run.source == "MapMyFitness"
