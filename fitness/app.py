from datetime import date
from typing import Self

from fastapi import FastAPI
import dotenv
from pydantic import BaseModel

from fitness.models import Run
from fitness.load import load_all_runs
from fitness.agg import (
    mileage_by_shoes,
    avg_miles_per_day,
    miles_by_day,
    total_mileage,
    rolling_sum,
)

# This is roughly when I started tracking my runs.
DEFAULT_START = date(2016, 1, 1)
DEFAULT_END = date.today()

dotenv.load_dotenv()
app = FastAPI()

runs: list[Run] | None = None


def get_runs() -> list[Run]:
    global runs
    if runs is None:
        runs = load_all_runs()
    return runs


# Run this once to load the runs before the first request.
get_runs()


@app.get("/runs")
def read_all_runs(start: date = DEFAULT_START, end: date = DEFAULT_END) -> list[Run]:
    """Get all runs."""
    runs = get_runs()
    if start is not None:
        runs = [run for run in runs if run.date >= start]
    if end is not None:
        runs = [run for run in runs if run.date <= end]
    return runs


@app.get("/metrics/mileage/total")
def read_total_mileage(start: date = DEFAULT_START, end: date = DEFAULT_END) -> float:
    """Get total mileage."""
    runs = get_runs()
    return total_mileage(runs, start, end)


class DayMileage(BaseModel):
    date: date
    mileage: float

    def __lt__(self, other: Self) -> bool:
        return self.date < other.date


@app.get("/metrics/mileage/by-day")
def read_mileage_by_day(
    start: date = DEFAULT_START, end: date = DEFAULT_END
) -> list[DayMileage]:
    """Get mileage by day."""
    runs = get_runs()
    tuples = miles_by_day(runs, start, end)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@app.get("/metrics/mileage/rolling-by-day")
def read_rolling_mileage_by_day(
    start: date = DEFAULT_START, end: date = DEFAULT_END, window: int = 1
) -> list[DayMileage]:
    """Get rolling sum of mileage over a window by day."""
    runs = get_runs()
    tuples = rolling_sum(runs, start, end, window)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@app.get("/metrics/mileage/avg-per-day")
def read_avg_miles_per_day(
    start: date = DEFAULT_START, end: date = DEFAULT_END
) -> float:
    """Get average mileage per day."""
    runs = get_runs()
    return avg_miles_per_day(runs, start, end)


class ShoeMileage(BaseModel):
    shoe: str
    mileage: float

    def __lt__(self, other: Self) -> bool:
        return self.mileage < other.mileage


@app.get("/metrics/mileage/by-shoe")
def read_miles_by_shoe() -> list[ShoeMileage]:
    """Get mileage by shoe."""
    runs = get_runs()
    mileage_as_dict = mileage_by_shoes(runs)
    results = [
        ShoeMileage(shoe=shoe_name, mileage=mileage)
        for shoe_name, mileage in mileage_as_dict.items()
    ]
    # Return the results sorted alphabetically by shoe name.
    results.sort(key=lambda x: x.shoe)
    return results
