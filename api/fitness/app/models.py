from typing import Literal, Self
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
