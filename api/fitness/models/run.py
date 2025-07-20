from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date, datetime, timezone
from typing import Self, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    # This prevents circular imports at runtime.
    from fitness.load.mmf import MmfActivity, MmfActivityType
    from fitness.load.strava import StravaActivityType, StravaActivityWithGear


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
    datetime_utc: datetime
    type: RunType
    distance: float  # in miles
    duration: float  # in seconds
    source: RunSource
    avg_heart_rate: float | None = None
    shoes: str | None = None
    
    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to include date field for backward compatibility."""
        data = super().model_dump(**kwargs)
        # Add the UTC date as 'date' field for backward compatibility
        data['date'] = self.datetime_utc.date()
        return data

    @classmethod
    def from_mmf(cls, mmf_run: MmfActivity) -> Self:
        # Use UTC date if available, otherwise fall back to original date
        workout_date = (
            mmf_run.workout_date_utc
            if mmf_run.workout_date_utc is not None
            else mmf_run.workout_date
        )
        # Create UTC datetime from the date (assuming start of day UTC)
        workout_datetime_utc = datetime.combine(workout_date, datetime.min.time()).replace(tzinfo=timezone.utc).replace(tzinfo=None)
        return cls(
            datetime_utc=workout_datetime_utc,
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
            datetime_utc=strava_run.start_date.replace(tzinfo=None),
            type=StravaActivityMap[strava_run.type],
            # Note that we need to convert the distance from meters to miles.
            distance=strava_run.distance_miles(),
            duration=strava_run.elapsed_time,
            avg_heart_rate=strava_run.average_heartrate,
            shoes=strava_run.shoes(),
            source="Strava",
        )
