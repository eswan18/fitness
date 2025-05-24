from datetime import date

import pytest

from fitness.load.run import Run
from fitness.agg.mileage import total_mileage, rolling_sum


@pytest.fixture
def sample_run():
    return Run(
        date=date(2023, 10, 1),
        type="Outdoor Run",
        distance=5.0,
        duration=1800,
        source="Strava",
        avg_heart_rate=150.0,
        shoes="Nike",
    )


def test_total_mileage(sample_run: Run):
    miles = total_mileage(
        [
            sample_run.model_copy(deep=True, update={"distance": 5.0}),
            sample_run.model_copy(deep=True, update={"distance": 3.0}),
            sample_run.model_copy(deep=True, update={"distance": 2.0}),
        ]
    )
    assert miles == 10.0


def test_rolling_sum(sample_run: Run):
    runs = [
        sample_run.model_copy(
            deep=True, update={"distance": 5.0, "date": date(2023, 10, 1)}
        ),
        sample_run.model_copy(
            deep=True, update={"distance": 3.0, "date": date(2023, 10, 2)}
        ),
        sample_run.model_copy(
            deep=True, update={"distance": 2.0, "date": date(2023, 10, 5)}
        ),
        sample_run.model_copy(
            deep=True, update={"distance": 2.0, "date": date(2023, 10, 6)}
        ),
    ]
    # Check a few different window sizes.
    window_1_results = rolling_sum(
        runs=runs, start=date(2023, 10, 1), end=date(2023, 10, 6), window=1
    )
    assert window_1_results == [
        (date(2023, 10, 1), 5),
        (date(2023, 10, 2), 3),
        (date(2023, 10, 3), 0),
        (date(2023, 10, 4), 0),
        (date(2023, 10, 5), 2),
        (date(2023, 10, 6), 2),
    ]
    window_2_results = rolling_sum(
        runs=runs, start=date(2023, 10, 1), end=date(2023, 10, 6), window=2
    )
    assert window_2_results == [
        (date(2023, 10, 1), 5),
        (date(2023, 10, 2), 8),
        (date(2023, 10, 3), 3),
        (date(2023, 10, 4), 0),
        (date(2023, 10, 5), 2),
        (date(2023, 10, 6), 4),
    ]
    window_3_results = rolling_sum(
        runs=runs, start=date(2023, 10, 1), end=date(2023, 10, 6), window=3
    )
    assert window_3_results == [
        (date(2023, 10, 1), 5),
        (date(2023, 10, 2), 8),
        (date(2023, 10, 3), 8),
        (date(2023, 10, 4), 3),
        (date(2023, 10, 5), 2),
        (date(2023, 10, 6), 4),
    ]
    # Make sure that runs outside the range are included if they are in the window.
    later_window = rolling_sum(
        runs=runs, start=date(2023, 10, 3), end=date(2023, 10, 6), window=3
    )
    assert later_window == [
        (date(2023, 10, 3), 8),
        (date(2023, 10, 4), 3),
        (date(2023, 10, 5), 2),
        (date(2023, 10, 6), 4),
    ]
