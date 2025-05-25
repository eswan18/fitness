from datetime import date

from fastapi import FastAPI, Depends
import dotenv

from fitness.models import Run
from .constants import DEFAULT_START, DEFAULT_END
from .dependencies import all_runs
from .metrics import router as metrics_router


dotenv.load_dotenv()
app = FastAPI()
app.include_router(metrics_router)

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
