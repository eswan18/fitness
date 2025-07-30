from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date, datetime, timezone
from typing import Self, Literal
import zoneinfo
import hashlib

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
    id: str  # Deterministic ID: Strava ID for Strava runs, hash for MMF runs
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
        if self.datetime_utc is not None:
            data["date"] = self.datetime_utc.date()
        else:
            # Fallback or warn about missing datetime
            print(f"Warning: Run missing datetime_utc: {data}")
            data["date"] = None
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
        workout_datetime_utc = (
            datetime.combine(workout_date, datetime.min.time())
            .replace(tzinfo=timezone.utc)
            .replace(tzinfo=None)
        )
        
        # Extract the workout ID from the MMF link
        # Link format: https://www.mapmyfitness.com/workout/{workout_id}
        import re
        link_match = re.search(r'/workout/(\d+)', mmf_run.link)
        if link_match:
            workout_id = link_match.group(1)
            deterministic_id = f"mmf_{workout_id}"
        else:
            # Fallback if link doesn't match expected format
            # This shouldn't happen, but provides safety
            fallback_components = [
                "mmf_fallback",
                mmf_run.date_submitted.isoformat(),
                workout_date.isoformat(),
                mmf_run.activity_type,
            ]
            fallback_string = "|".join(fallback_components)
            fallback_hash = hashlib.sha256(fallback_string.encode()).hexdigest()[:16]
            deterministic_id = f"mmf_fallback_{fallback_hash}"
        
        return cls(
            id=deterministic_id,
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
            id=f"strava_{strava_run.id}",  # Use Strava's ID with prefix
            datetime_utc=strava_run.start_date.replace(tzinfo=None),
            type=StravaActivityMap[strava_run.type],
            # Note that we need to convert the distance from meters to miles.
            distance=strava_run.distance_miles(),
            duration=strava_run.elapsed_time,
            avg_heart_rate=strava_run.average_heartrate,
            shoes=strava_run.shoes(),
            source="Strava",
        )


class LocalizedRun(Run):
    """A run with its datetime converted to user's local timezone."""

    localized_datetime: datetime

    @property
    def local_date(self) -> date:
        """Get the local date for this run."""
        return self.localized_datetime.date()

    @classmethod
    def from_run(cls, run: Run, user_timezone: str) -> Self:
        """Create a LocalizedRun from a Run by converting to user timezone."""
        tz = zoneinfo.ZoneInfo(user_timezone)

        # Convert UTC datetime to user's local timezone
        utc_aware = run.datetime_utc.replace(tzinfo=timezone.utc)
        localized_datetime = utc_aware.astimezone(tz).replace(tzinfo=None)

        return cls(
            id=run.id,
            datetime_utc=run.datetime_utc,
            localized_datetime=localized_datetime,
            type=run.type,
            distance=run.distance,
            duration=run.duration,
            source=run.source,
            avg_heart_rate=run.avg_heart_rate,
            shoes=run.shoes,
        )
