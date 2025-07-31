from typing import Literal, Self, Optional
from datetime import date

from pydantic import BaseModel


Sex = Literal["M", "F"]


class DayMileage(BaseModel):
    date: date
    mileage: float

    def __lt__(self, other: Self) -> bool:
        return self.date < other.date


class ShoeMileage(BaseModel):
    shoe: str
    mileage: float

    def __lt__(self, other: Self) -> bool:
        return self.mileage < other.mileage


class ShoeMileageWithRetirement(BaseModel):
    shoe: str
    mileage: float
    retired: bool
    retired_at: Optional[date] = None
    retirement_notes: Optional[str] = None

    def __lt__(self, other: Self) -> bool:
        return self.mileage < other.mileage


class RetireShoeRequest(BaseModel):
    retired_at: date
    retirement_notes: Optional[str] = None


class UpdateShoeRequest(BaseModel):
    """Request model for updating shoe properties via PATCH."""
    retired_at: Optional[date] = None
    retirement_notes: Optional[str] = None
