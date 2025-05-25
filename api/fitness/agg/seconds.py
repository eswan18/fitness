from datetime import date
from fitness.load import Run


def total_seconds(runs: list[Run], start: date, end: date) -> float:
    """
    Calculate the total seconds for a list of runs.
    """
    return sum(run.duration for run in runs if start <= run.date <= end)
