import logging

from fastapi import APIRouter

from fitness.app.models import Summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/", response_model=Summary)
def get_summary() -> Summary:
    """Get the summary of the fitness data."""
    return Summary(
        miles_all_time=1000,
        miles_this_calendar_month=100,
        miles_this_calendar_year=100,
        miles_last_30_days=100,
        miles_last_365_days=100,
    )
