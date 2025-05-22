from typing import Callable
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from fitness.ingest.strava.models import StravaActivity, ActivityAthlete, StravaGear
from fitness.ingest.strava import load_strava_runs


@pytest.fixture()
def make_sample_strava_activity() -> Callable[[], StravaActivity]:
    """Fixture to create a sample Strava activity."""
    id = 0

    def create_activity() -> StravaActivity:
        # Increment the ID for each new activity created.
        nonlocal id
        id += 1
        return StravaActivity(
            id=id,
            name="blah",
            resource_state=1,
            type="Run",
            commute=False,
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            start_date_local=datetime(2025, 1, 1, tzinfo=timezone.utc),
            timezone="UTC",
            utc_offset=0.0,
            distance=5000,
            moving_time=3600,
            elapsed_time=4000,
            total_elevation_gain=100,
            has_kudoed=False,
            has_heartrate=False,
            athlete=ActivityAthlete(id=1, resource_state=1),
            manual=False,
            kilojoules=None,
            start_latlng=[37.7749, -122.4194],
            end_latlng=[37.7749, -122.4194],
            achievement_count=0,
            kudos_count=0,
            comment_count=0,
            athlete_count=1,
            total_photo_count=0,
            max_speed=5.0,
            from_accepted_tag=False,
            sport_type="Run",
            trainer=False,
            photo_count=0,
            private=False,
            pr_count=0,
            heartrate_opt_out=False,
            average_speed=5.0,
            visibility="everyone",
        )

    return create_activity


@pytest.fixture()
def make_sample_strava_gear() -> Callable[[], StravaGear]:
    """Fixture to create a sample Strava gear."""
    id = 0

    def create_gear() -> StravaGear:
        # Increment the ID for each new gear created.
        nonlocal id
        id += 1
        return StravaGear(
            id=str(id),
            name="blah",
            nickname="blah",
            brand_name="Nike",
            model_name="Air Zoom",
            converted_distance=0.0,
            distance=0,
            notification_distance=0,
            primary=False,
            resource_state=1,
            retired=False,
        )

    return create_gear


def test_strava_load(make_sample_strava_activity, make_sample_strava_gear, monkeypatch):
    # Mock the StravaClient to avoid making real HTTP requests.
    mock_client = MagicMock()
    run = make_sample_strava_activity()
    run.type = "Run"
    run.gear_id = "1"
    indoor_run = make_sample_strava_activity()
    indoor_run.type = "Indoor Run"
    indoor_run.gear_id = "2"
    bike = make_sample_strava_activity()
    bike.type = "Ride"
    bike.gear_id = "3"
    mock_client.get_activities.return_value = [run, indoor_run, bike]

    # Set up mocking of the gear fetching.
    gear1 = make_sample_strava_gear()
    gear1.id = "1"
    gear1.nickname = "Brooks Shoes"
    gear2 = make_sample_strava_gear()
    gear2.id = "2"
    gear2.nickname = "Nike Shoes"
    mock_client.get_gear.return_value = [gear1, gear2]
    with monkeypatch.context() as m:
        m.setattr("fitness.ingest.strava.StravaClient.from_env", lambda: mock_client)
        runs = load_strava_runs()
    assert len(runs) == 2
    assert runs[0].gear.nickname == "Brooks Shoes"
    assert runs[1].gear.nickname == "Nike Shoes"

    mock_client.get_gear.assert_called_once_with({"1", "2"})
