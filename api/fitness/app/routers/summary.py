import logging

from fastapi import APIRouter

from fitness.app.models import TrmnlSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/trmnl", response_model=TrmnlSummary)
def get_trmnl_summary() -> TrmnlSummary:
    """Get the summary of the fitness data."""
    return TrmnlSummary(
        miles_all_time=1000,
        miles_this_calendar_month=100,
        miles_this_calendar_year=100,
        miles_last_30_days=100,
        miles_last_365_days=100,
    )
