from fastapi import FastAPI
from datetime import date

from fitness.models import Run
from fitness.load import load_all_runs
from fitness.agg import (
    mileage_by_shoes,
    avg_miles_per_day,
    miles_by_day,
    total_mileage,
    rolling_sum,
)

app = FastAPI()

runs: list[Run] | None = None


def get_runs() -> list[Run]:
    global runs
    if runs is None:
        runs = load_all_runs()
    return runs


@app.get("/runs")
def read_all_runs() -> list[Run]:
    """Get all runs."""
    return get_runs()


@app.get("/metrics/mileage/total")
def read_total_mileage(start: date, end: date) -> float:
    """Get total mileage."""
    runs = get_runs()
    return total_mileage(runs, start, end)


@app.get("/metrics/mileage/by-day")
def read_mileage_by_day(start: date, end: date) -> list[tuple[date, float]]:
    """Get mileage by day."""
    runs = get_runs()
    return miles_by_day(runs, start, end)


@app.get("/metrics/mileage/avg-per-day")
def read_avg_miles_per_day(start: date, end: date) -> float:
    """Get average mileage per day."""
    runs = get_runs()
    return avg_miles_per_day(runs, start, end)


@app.get("/metrics/mileage/rolling-by-day")
def read_rolling_mileage_by_day(
    start: date, end: date, window: int
) -> list[tuple[date, float]]:
    """Get rolling sum of mileage over a window by day."""
    runs = get_runs()
    return rolling_sum(runs, start, end, window)


@app.get("/metrics/mileage/by-shoe")
def read_miles_by_shoe() -> dict[str, float]:
    """Get mileage by shoe."""
    runs = get_runs()
    return mileage_by_shoes(runs)
