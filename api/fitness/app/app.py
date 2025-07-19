from datetime import date

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import dotenv

from fitness.models import Run
from .constants import DEFAULT_START, DEFAULT_END
from .dependencies import all_runs, refresh_runs_data
from .metrics import router as metrics_router


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
    runs: list[Run] = Depends(all_runs),
) -> list[Run]:
    """Get all runs."""
    if start is not None:
        runs = [run for run in runs if run.date >= start]
    if end is not None:
        runs = [run for run in runs if run.date <= end]
    return runs


@app.post("/refresh-data")
def refresh_data() -> dict[str, str | int]:
    """Refresh all runs data by clearing cache and reloading from sources."""
    refreshed_runs = refresh_runs_data()
    return {
        "status": "success",
        "message": "Data refreshed successfully",
        "total_runs": len(refreshed_runs)
    }
