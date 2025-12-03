from typing import Literal, Self, Optional
from datetime import date

from pydantic import BaseModel

from .env_loader import EnvironmentName


Sex = Literal["M", "F"]  # Biological sex used for HR-based training load formulas


class TrmnlSummary(BaseModel):
    """Response model for the summary endpoint."""

    miles_all_time: float
    miles_this_calendar_month: float
    miles_this_calendar_year: float
    miles_last_30_days: float
    miles_last_365_days: float


class DayMileage(BaseModel):
    """Mileage aggregated for a single day."""

    date: date
    mileage: float

    def __lt__(self, other: Self) -> bool:
        return self.date < other.date


class RetireShoeRequest(BaseModel):
    """Request model to retire a shoe on a specific date."""

    retired_at: date
    retirement_notes: Optional[str] = None


class UpdateShoeRequest(BaseModel):
    """Request model for updating shoe properties via PATCH."""

    retired_at: Optional[date] = None
    retirement_notes: Optional[str] = None


class EnvironmentResponse(BaseModel):
    """Response model for the environment endpoint."""

    environment: EnvironmentName
