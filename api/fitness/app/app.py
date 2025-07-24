from datetime import date, datetime
from typing import Literal

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import dotenv

from fitness.models import Run
from .constants import DEFAULT_START, DEFAULT_END
from .dependencies import all_runs, refresh_runs_data
from .metrics import router as metrics_router
from fitness.utils.timezone import filter_runs_by_local_date_range, convert_runs_to_user_timezone

RunSortBy = Literal["date", "distance", "duration", "pace", "source", "type", "shoes"]
SortOrder = Literal["asc", "desc"]


dotenv.load_dotenv()
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
        filtered_runs = [run for run in localized_runs if start <= run.local_date <= end]
    
    # Apply sorting to filtered runs
    return sort_runs(filtered_runs, sort_by, sort_order)


def sort_runs(runs: list[Run], sort_by: RunSortBy, sort_order: SortOrder) -> list[Run]:
    """Sort runs by the specified field and order."""
    reverse = sort_order == "desc"
    
    def get_sort_key(run):
        if sort_by == "date":
            # Use localized_datetime for LocalizedRun, otherwise datetime_utc
            return getattr(run, 'localized_datetime', run.datetime_utc)
        elif sort_by == "distance":
            return run.distance
        elif sort_by == "duration":
            return run.duration
        elif sort_by == "pace":
            # Calculate pace (minutes per mile) - avoid division by zero
            if run.distance > 0:
                return (run.duration / 60) / run.distance
            return float('inf')  # Put zero-distance runs at the end
        elif sort_by == "source":
            return run.source
        elif sort_by == "type":
            return run.type
        elif sort_by == "shoes":
            return run.shoes or ""  # Handle None values
        else:
            # Default to date if unknown sort field
            return getattr(run, 'localized_datetime', run.datetime_utc)
    
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
