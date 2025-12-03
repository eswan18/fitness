import logging
from datetime import date, timedelta

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

    # This way of calculating today will be "wrong" relative to the user's timezone, but only noticeable at the ends of months and years.
    today = date.today()
    current_month_name = today.strftime("%B")
    current_year = today.year

    # Calendar month and year totals
    month_start = today.replace(day=1)
    year_start = today.replace(day=1, month=1)
    miles_this_calendar_month = int(total_mileage(runs, month_start, date.max))
    miles_this_calendar_year = int(total_mileage(runs, year_start, date.max))
    # Last 30 and 365 days totals
    last_30_days_start = today - timedelta(days=30)
    last_365_days_start = today - timedelta(days=365)
    miles_last_30_days = int(total_mileage(runs, last_30_days_start, date.max))
    miles_last_365_days = int(total_mileage(runs, last_365_days_start, date.max))

    return TrmnlSummary(
        miles_all_time=miles_all_time,
        minutes_all_time=minutes_all_time,
        miles_this_calendar_month=miles_this_calendar_month,
        calendar_month_name=current_month_name,
        miles_this_calendar_year=miles_this_calendar_year,
        calendar_year_name=current_year,
        miles_last_30_days=miles_last_30_days,
        miles_last_365_days=miles_last_365_days,
    )
