from collections import deque
from datetime import timedelta, date

from fitness.load.run import Run


def total_mileage(runs: list[Run]):
    """
    Calculate the total mileage for a list of runs.
    """
    return sum(run.distance for run in runs)


def rolling_sum(
    runs: list[Run], start: date, end: date, window: int
) -> list[tuple[date, float]]:
    """
    Calculate the rolling sum of distances for a list of runs.

    The rolling sum is calculated over a window of the previous `window` days, including
    the current day. Returns a list of (day, window_sum).
    """
    # 1. Bucket runs into miles-per-day
    miles_per_day: dict[date, float] = {}
    for r in runs:
        miles_per_day.setdefault(r.date, 0.0)
        miles_per_day[r.date] += r.distance

    # 2. Prepare sliding-window state
    result: list[tuple[date, float]] = []
    window_deque: deque[tuple[date, float]] = deque()
    window_sum = 0.0

    # 3. Walk each day in the [start, end] range
    total_days = (end - start).days + 1
    for offset in range(total_days):
        today = start + timedelta(days=offset)
        today_miles = miles_per_day.get(today, 0.0)

        # Add today's miles
        window_deque.append((today, today_miles))
        window_sum += today_miles

        # Evict days older than the window
        cutoff = today - timedelta(days=window - 1)
        while window_deque and window_deque[0][0] < cutoff:
            _old_date, old_miles = window_deque.popleft()
            window_sum -= old_miles

        result.append((today, window_sum))

    return result
