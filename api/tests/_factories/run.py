from typing import Any, Mapping
from datetime import date, datetime, timezone
from fitness.models import Run


class RunFactory:
    def __init__(self, run: Run | None = None):
        if run is None:
            run = Run(
                date=date(2023, 10, 1),
                datetime_utc=datetime(2023, 10, 1, 12, 0, 0),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
                avg_heart_rate=150.0,
                shoes="Nike",
            )
        self.run = run

    def make(self, update: Mapping[str, Any] | None = None) -> Run:
        run = self.run.model_copy(deep=True, update=update)
        # If date was updated but datetime_utc wasn't, sync datetime_utc to match date
        if update and "date" in update and "datetime_utc" not in update:
            new_date = update["date"]
            run.datetime_utc = datetime.combine(new_date, datetime.min.time())
        return run
