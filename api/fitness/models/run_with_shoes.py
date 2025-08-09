from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RunWithShoes(BaseModel):
    """A run with explicit shoe information, guaranteed to be present."""

    id: str
    datetime_utc: datetime
    type: str  # RunType from Run model
    distance: float  # in miles
    duration: float  # in seconds
    source: str  # RunSource from Run model
    avg_heart_rate: Optional[float] = None
    shoe_id: Optional[str] = None
    shoes: Optional[str] = None  # Shoe name - always included, can be None
    deleted_at: Optional[datetime] = None

    @property
    def is_deleted(self) -> bool:
        """Check if the run is soft-deleted."""
        return self.deleted_at is not None

    @property
    def date(self):
        """Get the UTC date for backward compatibility."""
        return self.datetime_utc.date() if self.datetime_utc else None

    @classmethod
    def from_run_and_shoe_name(cls, run, shoe_name: Optional[str] = None):
        """Create a RunWithShoes from a Run and optional shoe name."""
        # Use the provided shoe_name, or try to get it from the run
        shoes = shoe_name if shoe_name is not None else run.shoe_name

        return cls(
            id=run.id,
            datetime_utc=run.datetime_utc,
            type=run.type,
            distance=run.distance,
            duration=run.duration,
            source=run.source,
            avg_heart_rate=run.avg_heart_rate,
            shoe_id=run.shoe_id,
            shoes=shoes,
            deleted_at=run.deleted_at,
        )
