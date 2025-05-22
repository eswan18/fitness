from datetime import date
from typing import Self
from dataclasses import dataclass

from .mmf import MmfRun


@dataclass
class Run:
    date: date
    distance: float
    duration: float
    average_speed: float
    shoes: str

    @classmethod
    def from_mmf(cls, mmf_run: MmfRun) -> Self:
        return cls(
            date=mmf_run.workout_date,
            distance=mmf_run.distance,
            duration=mmf_run.workout_time,
            average_speed=mmf_run.avg_speed,
            shoes=mmf_run.shoes,
        )