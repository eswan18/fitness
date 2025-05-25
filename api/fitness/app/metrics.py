from datetime import date

from fastapi import APIRouter, Depends

from fitness.agg import (
    mileage_by_shoes,
    avg_miles_per_day,
    miles_by_day,
    total_mileage,
    rolling_sum,
)
from fitness.app.constants import DEFAULT_START, DEFAULT_END
from fitness.app.dependencies import all_runs
from fitness.models import Run
from .models import DayMileage, ShoeMileage

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/mileage/total")
def read_total_mileage(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    runs: list[Run] = Depends(all_runs),
) -> float:
    """Get total mileage."""
    return total_mileage(runs, start, end)


@router.get("/mileage/by-day")
def read_mileage_by_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    runs: list[Run] = Depends(all_runs),
) -> list[DayMileage]:
    """Get mileage by day."""
    tuples = miles_by_day(runs, start, end)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@router.get("/mileage/rolling-by-day")
def read_rolling_mileage_by_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    window: int = 1,
    runs: list[Run] = Depends(all_runs),
) -> list[DayMileage]:
    """Get rolling sum of mileage over a window by day."""
    tuples = rolling_sum(runs, start, end, window)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@router.get("/mileage/avg-per-day")
def read_avg_miles_per_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    runs: list[Run] = Depends(all_runs),
) -> float:
    """Get average mileage per day."""
    return avg_miles_per_day(runs, start, end)


@router.get("/mileage/by-shoe")
def read_miles_by_shoe(runs: list[Run] = Depends(all_runs)) -> list[ShoeMileage]:
    """Get mileage by shoe."""
    mileage_as_dict = mileage_by_shoes(runs)
    results = [
        ShoeMileage(shoe=shoe_name, mileage=mileage)
        for shoe_name, mileage in mileage_as_dict.items()
    ]
    # Return the results sorted alphabetically by shoe name.
    results.sort(key=lambda x: x.shoe)
    return results
