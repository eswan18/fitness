from datetime import date, datetime, timezone

import pytest

from fitness.models import Run
from tests._factories import StravaActivityWithGearFactory


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
    assert run.date == date(2024, 11, 4)
    assert run.type == "Outdoor Run"
    assert run.distance == pytest.approx(5)
    assert run.duration == 1800
    assert run.avg_heart_rate == 150.0
    assert run.shoes == activity.gear.nickname
    assert run.source == "Strava"