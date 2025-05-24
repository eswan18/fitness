from datetime import date
from typing import Self, Literal

from pydantic import BaseModel

from .mmf import MmfActivity, MmfActivityType, load_mmf_runs
from .strava import StravaActivityType, StravaActivityWithGear, load_strava_runs


RunType = Literal["Outdoor Run", "Treadmill Run"]
RunSource = Literal["MapMyFitness", "Strava"]

# Map the MMF activity types to our run types.
MmfActivityMap: dict[MmfActivityType, RunType] = {
    "Indoor Run / Jog": "Treadmill Run",
    "Run": "Outdoor Run",
}
# Map the Strava activity types to our run types.
StravaActivityMap: dict[StravaActivityType, RunType] = {
    "Run": "Outdoor Run",
    "Indoor Run": "Treadmill Run",
}


class Run(BaseModel):
    date: date
    type: RunType
    distance: float  # in miles
    duration: float  # in seconds
    source: RunSource
    avg_heart_rate: float | None = None
    shoes: str | None = None

    @classmethod
    def from_mmf(cls, mmf_run: MmfActivity) -> Self:
        return cls(
            date=mmf_run.workout_date,
            type=MmfActivityMap[mmf_run.activity_type],
            distance=mmf_run.distance,
            duration=mmf_run.workout_time,
            avg_heart_rate=mmf_run.avg_heart_rate,
            shoes=mmf_run.shoes(),
            source="MapMyFitness",
        )

    @classmethod
    def from_strava(cls, strava_run: StravaActivityWithGear) -> Self:
        return cls(
            date=strava_run.start_date.date(),
            type=StravaActivityMap[strava_run.type],
            # Note that we need to convert the distance from meters to miles.
            distance=strava_run.distance_miles(),
            duration=strava_run.elapsed_time,
            avg_heart_rate=strava_run.average_heartrate,
            shoes=strava_run.shoes(),
            source="Strava",
        )


def load_all_runs() -> list[Run]:
    """Get all runs from Strava and MMF."""
    mmf_runs = [Run.from_mmf(mmf_run) for mmf_run in load_mmf_runs()]
    strava_runs = [Run.from_strava(strava_run) for strava_run in load_strava_runs()]
    return mmf_runs + strava_runs
