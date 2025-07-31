from datetime import date

from fastapi import APIRouter, Depends

from fitness.agg import (
    mileage_by_shoes,
    mileage_by_shoes_with_retirement,
    avg_miles_per_day,
    miles_by_day,
    total_mileage,
    rolling_sum,
    total_seconds,
    training_stress_balance,
)
from fitness.agg.training_load import trimp_by_day
from fitness.app.constants import DEFAULT_START, DEFAULT_END
from fitness.app.dependencies import all_runs
from fitness.models import Run, Sex, DayTrainingLoad
from .models import (
    DayMileage,
    ShoeMileage,
    ShoeMileageWithRetirement,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/seconds/total")
def read_total_seconds(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> float:
    """Get total seconds."""
    return total_seconds(runs, start, end, user_timezone)


@router.get("/mileage/total")
def read_total_mileage(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> float:
    """Get total mileage."""
    return total_mileage(runs, start, end, user_timezone)


@router.get("/mileage/by-day")
def read_mileage_by_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> list[DayMileage]:
    """Get mileage by day."""
    tuples = miles_by_day(runs, start, end, user_timezone)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@router.get("/mileage/rolling-by-day")
def read_rolling_mileage_by_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    window: int = 1,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> list[DayMileage]:
    """Get rolling sum of mileage over a window by day."""
    tuples = rolling_sum(runs, start, end, window, user_timezone)
    results = [DayMileage(date=day, mileage=miles) for (day, miles) in tuples]
    return results


@router.get("/mileage/avg-per-day")
def read_avg_miles_per_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> float:
    """Get average mileage per day."""
    return avg_miles_per_day(runs, start, end, user_timezone)


@router.get("/mileage/by-shoe")
def read_miles_by_shoe(
    include_retired: bool = False, runs: list[Run] = Depends(all_runs)
) -> list[ShoeMileage]:
    """Get mileage by shoe."""
    mileage_as_dict = mileage_by_shoes(runs, include_retired=include_retired)
    results = [
        ShoeMileage(shoe=shoe_name, mileage=mileage)
        for shoe_name, mileage in mileage_as_dict.items()
    ]
    # Return the results sorted alphabetically by shoe name.
    results.sort(key=lambda x: x.shoe)
    return results


@router.get("/mileage/by-shoe-with-retirement")
def read_miles_by_shoe_with_retirement(
    runs: list[Run] = Depends(all_runs),
) -> list[ShoeMileageWithRetirement]:
    """Get mileage by shoe with retirement information."""
    mileage_with_retirement = mileage_by_shoes_with_retirement(runs)
    results = [
        ShoeMileageWithRetirement(
            shoe=shoe_name,
            mileage=info["mileage"],
            retired=info["retired"],
            retired_at=info["retired_at"],
            retirement_notes=info["retirement_notes"],
        )
        for shoe_name, info in mileage_with_retirement.items()
    ]
    # Return the results sorted alphabetically by shoe name.
    results.sort(key=lambda x: x.shoe)
    return results


@router.get("/training-load/by-day")
def read_training_load_by_day(
    start: date,
    end: date,
    max_hr: float,
    resting_hr: float,
    sex: Sex,
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> list[DayTrainingLoad]:
    """Get training load by day."""
    return training_stress_balance(
        runs=runs,
        max_hr=max_hr,
        resting_hr=resting_hr,
        sex=sex,
        start_date=start,
        end_date=end,
        user_timezone=user_timezone,
    )


@router.get("/trimp/by-day")
def read_trimp_by_day(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    max_hr: float = 192,
    resting_hr: float = 42,
    sex: Sex = "M",
    user_timezone: str | None = None,
    runs: list[Run] = Depends(all_runs),
) -> list[dict]:
    """Get TRIMP values by day."""
    day_trimps = trimp_by_day(runs, start, end, max_hr, resting_hr, sex, user_timezone)
    return [{"date": dt.date, "trimp": dt.trimp} for dt in day_trimps]
