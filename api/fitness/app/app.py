# This file loads env variables and must thus be imported before anything else.
from . import env_loader  # noqa: F401
from .env_loader import get_current_environment

import os
import logging
from datetime import date, datetime
from typing import Literal, TypeVar, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from fitness.models import Run
from fitness.models.run_detail import RunDetail
from .constants import DEFAULT_START, DEFAULT_END
from .dependencies import all_runs, update_new_runs_only
from .metrics import router as metrics_router
from .shoe_routes import router as shoe_router
from .run_edit_routes import router as run_edit_router
from .sync_routes import router as sync_router
from .models import EnvironmentResponse
from fitness.utils.timezone import convert_runs_to_user_timezone

"""FastAPI application setup for the fitness API.

Exposes routes for reading runs, runs-with-shoes, metrics, shoe management,
run editing, and updating data from external sources. This module configures
CORS, logging behavior, and provides helper types for sorting.
"""

RunSortBy = Literal[
    "date", "distance", "duration", "pace", "heart_rate", "source", "type", "shoes"
]
SortOrder = Literal["asc", "desc"]

# Type variable for generic sorting function
# Supports Run and RunDetail (which shares the sorted fields)
T = TypeVar("T", Run, RunDetail)

app = FastAPI()
app.include_router(metrics_router)
app.include_router(shoe_router)
app.include_router(run_edit_router)
app.include_router(sync_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configure basic logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Configure the logging for the API itself if the user specifies it.
if "LOG_LEVEL" in os.environ:
    match os.environ["LOG_LEVEL"].upper():
        case "DEBUG":
            log_level = logging.DEBUG
        case "INFO":
            log_level = logging.INFO
        case "WARNING":
            log_level = logging.WARNING
        case "ERROR":
            log_level = logging.ERROR
        case "CRITICAL":
            log_level = logging.CRITICAL
        case _:
            raise ValueError(f"Invalid log level: {os.environ['LOG_LEVEL']}")
    logging.getLogger("fitness").setLevel(log_level)


@app.get("/runs", response_model=list[Run])
def read_all_runs(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    sort_by: RunSortBy = "date",
    sort_order: SortOrder = "desc",
    runs: list[Run] = Depends(all_runs),
) -> list[Run]:
    """Get all runs with optional sorting.

    Args:
        start: Inclusive start date for filtering (local to `user_timezone` if provided).
        end: Inclusive end date for filtering (local to `user_timezone` if provided).
        user_timezone: IANA timezone for local-date filtering and display. If None, use UTC dates.
        sort_by: Field to sort by (date, distance, duration, pace, heart_rate, source, type, shoes).
        sort_order: Sort order, ascending or descending.
        runs: Dependency injection of all runs from the database.
    """
    # Filter first to get the right date range
    if user_timezone is None:
        # Simple UTC filtering
        filtered_runs = [run for run in runs if start <= run.datetime_utc.date() <= end]
    else:
        # Convert to user timezone and filter by local dates
        localized_runs = convert_runs_to_user_timezone(runs, user_timezone)
        filtered_runs = [
            run for run in localized_runs if start <= run.local_date <= end
        ]

    # Apply sorting to filtered runs
    return sort_runs_generic(filtered_runs, sort_by, sort_order)


# Removed legacy /runs-with-shoes in favor of /runs-details


@app.get("/runs/details", response_model=list[RunDetail])
def read_run_details(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    sort_by: RunSortBy = "date",
    sort_order: SortOrder = "desc",
) -> list[RunDetail]:
    """Get detailed runs with shoes and sync info.

    Uses server-side date filtering and ordering by UTC datetime for efficiency.
    """
    from fitness.db.runs import get_run_details_in_date_range, get_all_run_details

    # Get run details from database
    if start != DEFAULT_START or end != DEFAULT_END:
        details = get_run_details_in_date_range(start, end)
    else:
        details = get_all_run_details()

    # Apply sorting
    # Reuse sort_runs_generic since RunDetail is compatible on the used fields
    return sort_runs_generic(details, sort_by, sort_order)


# Avoid potential ambiguity with dynamic route `/runs/{run_id}` in some setups
# by providing an alternate, unambiguous path for the same data.
@app.get("/runs-details", response_model=list[RunDetail])
def read_run_details_alt(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    sort_by: RunSortBy = "date",
    sort_order: SortOrder = "desc",
) -> list[RunDetail]:
    return read_run_details(start=start, end=end, sort_by=sort_by, sort_order=sort_order)


def sort_runs_generic(
    runs: list[T], sort_by: RunSortBy, sort_order: SortOrder
) -> list[T]:
    """Sort runs by the specified field and order.

    Works with both `Run` and `RunDetail` types.
    """
    reverse = sort_order == "desc"

    def get_sort_key(run: T) -> Any:
        if sort_by == "date":
            # Use localized_datetime for LocalizedRun, otherwise datetime_utc
            return getattr(run, "localized_datetime", run.datetime_utc)
        elif sort_by == "distance":
            return run.distance
        elif sort_by == "duration":
            return run.duration
        elif sort_by == "pace":
            # Calculate pace (minutes per mile) - avoid division by zero
            if run.distance > 0:
                return (run.duration / 60) / run.distance
            return float("inf")  # Put zero-distance runs at the end
        elif sort_by == "heart_rate":
            return (
                run.avg_heart_rate or 0
            )  # Handle None values, put them first when asc
        elif sort_by == "source":
            return run.source
        elif sort_by == "type":
            return run.type
        elif sort_by == "shoes":
            # Handle RunDetail (shoes) and base Run (shoe_name)
            if hasattr(run, "shoes"):
                return getattr(run, "shoes") or ""
            else:
                return getattr(run, "shoe_name", None) or ""
        else:
            # Default to date if unknown sort field
            return getattr(run, "localized_datetime", run.datetime_utc)

    return sorted(runs, key=get_sort_key, reverse=reverse)


@app.get("/environment", response_model=EnvironmentResponse)
def get_environment() -> EnvironmentResponse:
    """Get the current environment configuration."""
    environment = get_current_environment()
    return EnvironmentResponse(environment=environment)


@app.post("/update-data", response_model=dict)
def update_data() -> dict:
    """Fetch data from external sources and insert only new runs not in database.

    Returns a summary including counts of external runs, existing DB runs, new
    runs found and inserted, and IDs of newly inserted runs.
    """
    result = update_new_runs_only()
    result.update(
        {
            "status": "success",
            "message": f"Found {result['new_runs_found']} new runs, inserted {result['new_runs_inserted']}",
            "updated_at": datetime.now().isoformat(),
        }
    )
    return result
