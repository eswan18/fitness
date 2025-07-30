import os
from dotenv import load_dotenv

# Load env vars before any app code runs.
env = os.getenv("ENV", "dev")
if env not in ("dev", "prod"):
    raise ValueError(f"Invalid environment: {env}")
load_dotenv(f".env.{env}", verbose=True)

from datetime import date, datetime
from typing import Literal

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from fitness.models import Run
from .constants import DEFAULT_START, DEFAULT_END
from .dependencies import all_runs, refresh_runs_data
from .metrics import router as metrics_router
from fitness.utils.timezone import convert_runs_to_user_timezone

RunSortBy = Literal["date", "distance", "duration", "pace", "heart_rate", "source", "type", "shoes"]
SortOrder = Literal["asc", "desc"]


app = FastAPI()
app.include_router(metrics_router)

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

runs: list[Run] | None = None


# Run this once to load & cache the runs data before the first request.
all_runs()


@app.get("/runs")
def read_all_runs(
    start: date = DEFAULT_START,
    end: date = DEFAULT_END,
    user_timezone: str | None = None,
    sort_by: RunSortBy = "date",
    sort_order: SortOrder = "desc",
    runs: list[Run] = Depends(all_runs),
) -> list[Run]:
    """Get all runs with optional sorting."""
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
    return sort_runs(filtered_runs, sort_by, sort_order)


def sort_runs(runs: list[Run], sort_by: RunSortBy, sort_order: SortOrder) -> list[Run]:
    """Sort runs by the specified field and order."""
    reverse = sort_order == "desc"

    def get_sort_key(run):
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
            return run.avg_heart_rate or 0  # Handle None values, put them first when asc
        elif sort_by == "source":
            return run.source
        elif sort_by == "type":
            return run.type
        elif sort_by == "shoes":
            return run.shoes or ""  # Handle None values
        else:
            # Default to date if unknown sort field
            return getattr(run, "localized_datetime", run.datetime_utc)

    try:
        return sorted(runs, key=get_sort_key, reverse=reverse)
    except (TypeError, AttributeError) as e:
        # If sorting fails, return unsorted runs and log the error
        print(f"Warning: Failed to sort runs by {sort_by}: {e}")
        return runs


@app.post("/refresh-data")
def refresh_data() -> dict[str, str | int]:
    """Refresh all runs data by clearing cache and reloading from sources."""
    refreshed_runs = refresh_runs_data()
    return {
        "status": "success",
        "message": "Data refreshed successfully",
        "total_runs": len(refreshed_runs),
        "refreshed_at": datetime.now().isoformat(),
    }
