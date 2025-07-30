"""Database models using SQLModel for the fitness app."""

from __future__ import annotations
from typing import TYPE_CHECKING, Self, Literal
from datetime import datetime, date, timezone
import zoneinfo

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

if TYPE_CHECKING:
    # This prevents circular imports at runtime.
    from fitness.load.mmf import MmfActivity, MmfActivityType
    from fitness.load.strava import StravaActivityType, StravaActivityWithGear

# Unified type definitions (moved from run.py)
RunType = Literal["Outdoor Run", "Treadmill Run"]
RunSource = Literal["MapMyFitness", "Strava"]

# Map the MMF activity types to our run types.
MmfActivityMap: dict["MmfActivityType", RunType] = {
    "Indoor Run / Jog": "Treadmill Run",
    "Run": "Outdoor Run",
}
# Map the Strava activity types to our run types.
StravaActivityMap: dict["StravaActivityType", RunType] = {
    "Run": "Outdoor Run",
    "Indoor Run": "Treadmill Run",
}


class RunBase(SQLModel):
    """Base run model with shared fields and methods."""
    
    datetime_utc: datetime = Field(index=True)
    type: RunType
    distance: float = Field(description="Distance in miles")
    duration: float = Field(description="Duration in seconds") 
    source: RunSource = Field(index=True)
    avg_heart_rate: float | None = Field(default=None)
    shoes: str | None = Field(default=None, index=True)
    
    model_config = ConfigDict(from_attributes=True)

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
    def from_mmf(cls, mmf_run: "MmfActivity") -> Self:
        """Create a Run from MMF activity data."""
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
    def from_strava(cls, strava_run: "StravaActivityWithGear") -> Self:
        """Create a Run from Strava activity data."""
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


class RunTable(RunBase, table=True):
    """Database model for runs table."""
    
    __tablename__ = "runs"
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Timestamps for tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Run(RunBase):
    """
    Unified Run model for API responses and general use.
    This replaces the old Pydantic Run model.
    """
    pass


class RunCreate(RunBase):
    """Model for creating a new run (no id, timestamps auto-generated)."""
    pass


class RunRead(RunBase):
    """Model for reading a run (includes all fields including id and timestamps)."""
    id: int
    created_at: datetime
    updated_at: datetime


class RunUpdate(SQLModel):
    """Model for updating a run (all fields optional)."""
    datetime_utc: datetime | None = None
    type: RunType | None = None
    distance: float | None = None
    duration: float | None = None
    source: RunSource | None = None
    avg_heart_rate: float | None = None
    shoes: str | None = None


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
            datetime_utc=run.datetime_utc,
            localized_datetime=localized_datetime,
            type=run.type,
            distance=run.distance,
            duration=run.duration,
            source=run.source,
            avg_heart_rate=run.avg_heart_rate,
            shoes=run.shoes,
        )