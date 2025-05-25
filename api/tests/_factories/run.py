from typing import Any, Mapping
from datetime import date
from fitness.models import Run


class RunFactory:
    def __init__(self, run: Run | None = None):
        if run is None:
            run = Run(
                date=date(2023, 10, 1),
                type="Outdoor Run",
                distance=5.0,
                duration=1800,
                source="Strava",
                avg_heart_rate=150.0,
                shoes="Nike",
            )
        self.run = run

    def make(self, update: Mapping[str, Any] | None = None) -> Run:
        return self.run.model_copy(deep=True, update=update)
