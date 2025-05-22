from datetime import date
from typing import Self, Literal
from dataclasses import dataclass

from .mmf import MmfActivity, MmfActivityType
from .strava import StravaActivityType

RunType = Literal["Outdoor Run", "Treadmill Run"]

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


@dataclass
class Run:
    date: date
    type: RunType
    distance: float
    duration: float
    average_speed: float
    shoes: str | None = None

    @classmethod
    def from_mmf(cls, mmf_run: MmfActivity) -> Self:
        return cls(
            date=mmf_run.workout_date,
            type=MmfActivityMap[mmf_run.activity_type],
            distance=mmf_run.distance,
            duration=mmf_run.workout_time,
            average_speed=mmf_run.avg_speed,
            shoes=mmf_run.shoes(),
        )
