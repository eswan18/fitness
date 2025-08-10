from typing import Literal, Self, Optional
from datetime import date

from pydantic import BaseModel


Sex = Literal["M", "F"]  # Biological sex used for HR-based training load formulas
Environment = Literal["dev", "prod"]  # Application environment


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

    environment: Environment
