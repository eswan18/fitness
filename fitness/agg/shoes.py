from fitness.load import Run

def mileage_by_shoes(runs: list[Run]) -> dict[str, float]:
    """
    Calculate the total mileage for each pair of shoes used in the runs.
    """
    mileage: dict[str, float] = {}
    for run in runs:
        if run.shoes is None:
            continue
        mileage[run.shoes] = mileage.get(run.shoes, 0.0) + run.distance
    return mileage
