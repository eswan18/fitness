from __future__ import annotations
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from .run import RunType, RunSource


class RunWithShoes(BaseModel):
    """A run with explicit shoe information, guaranteed to be present.

    This mirrors the core `Run` fields while always exposing a `shoes` field
    that contains the human-readable shoe name if known (or None).
    """

    id: str
    datetime_utc: datetime
    type: RunType  # RunType from Run model
    distance: float  # in miles
    duration: float  # in seconds
    source: RunSource  # RunSource from Run model
    avg_heart_rate: Optional[float] = None
    shoe_id: Optional[str] = None
    shoes: Optional[str] = None  # Shoe name - always included, can be None
    deleted_at: Optional[datetime] = None

    @property
    def is_deleted(self) -> bool:
        """Check if the run is soft-deleted."""
        return self.deleted_at is not None

    @property
    def date(self) -> Optional[date]:
        """Get the UTC date for backward compatibility."""
        return self.datetime_utc.date() if self.datetime_utc else None

    @classmethod
    def from_run_and_shoe_name(cls, run, shoe_name: Optional[str] = None) -> "RunWithShoes":
        """Create a RunWithShoes from a Run and optional shoe name.

        Args:
            run: The base run instance to augment.
            shoe_name: Optional explicit shoe name to use. If not provided, the
                method will use `run.shoe_name` if available.
        """
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
