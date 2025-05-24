from collections import deque
from datetime import timedelta, date

from fitness.load import Run


def total_mileage(runs: list[Run]):
    """
    Calculate the total mileage for a list of runs.
    """
    return sum(run.distance for run in runs)


def avg_miles_per_day(runs: list[Run], start: date, end: date) -> float:
    """
    Calculate the average mileage per day for a list of runs in the range [start, end].
    """
    total_days = (end - start).days + 1
    if total_days <= 0:
        return 0.0
    return total_mileage(runs) / total_days


def miles_by_day(runs: list[Run], start: date, end: date) -> list[tuple[date, float]]:
    """
    Calculate the total mileage for each day in the range [start, end].
    """
    return rolling_sum(runs, start, end, window=1)


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

    # 2. Determine the first day we need to consider
    #    (so that runs up to `window-1` days before `start` are counted)
    initial_date = start - timedelta(days=window - 1)

    result: list[tuple[date, float]] = []
    window_deque: deque[tuple[date, float]] = deque()
    window_sum = 0.0

    # 3. Walk each day from initial_date up through `end`
    total_days = (end - initial_date).days + 1
    for offset in range(total_days):
        today = initial_date + timedelta(days=offset)
        today_miles = miles_per_day.get(today, 0.0)

        # add today's miles into the window
        window_deque.append((today, today_miles))
        window_sum += today_miles

        # evict anything older than `window` days
        cutoff = today - timedelta(days=window - 1)
        while window_deque and window_deque[0][0] < cutoff:
            old_date, old_miles = window_deque.popleft()
            window_sum -= old_miles

        # only start recording once we're at or past the user’s `start` date
        if today >= start:
            result.append((today, window_sum))

    return result
