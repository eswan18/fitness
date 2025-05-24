from typing import Any, Mapping
from datetime import date
import pytest

from fitness.load import Run


class RunFactory:
    def __init__(self, run: Run):
        self.run = run

    def make(self, update: Mapping[str, Any] | None = None) -> Run:
        return self.run.model_copy(deep=True, update=update)


@pytest.fixture(scope="session")
def run_factory() -> RunFactory:
    run = Run(
        date=date(2023, 10, 1),
        type="Outdoor Run",
        distance=5.0,
        duration=1800,
        source="Strava",
        avg_heart_rate=150.0,
        shoes="Nike",
    )
    return RunFactory(run=run)
