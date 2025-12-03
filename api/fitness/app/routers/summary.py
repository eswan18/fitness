import logging
from datetime import date

from fastapi import APIRouter, Depends

from fitness.app.models import TrmnlSummary
from fitness.app.dependencies import all_runs
from fitness.agg import total_mileage, total_seconds
from fitness.models import Run

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/trmnl", response_model=TrmnlSummary)
def get_trmnl_summary(runs: list[Run] = Depends(all_runs)) -> TrmnlSummary:
    """Get the summary of the fitness data."""
    # Calculate all-time totals using aggregation functions with full date range
    miles_all_time = int(total_mileage(runs, date.min, date.max))
    minutes_all_time = int(total_seconds(runs, date.min, date.max) / 60)

    return TrmnlSummary(
        miles_all_time=miles_all_time,
        minutes_all_time=minutes_all_time,
        miles_this_calendar_month=100,
        miles_this_calendar_year=100,
        miles_last_30_days=100,
        miles_last_365_days=100,
    )
