from fitness.models import Run
from .mmf import load_mmf_runs
from .strava import load_strava_runs
from .strava.client import StravaClient


def load_all_runs(strava_client: StravaClient | None = None) -> list[Run]:
    """Get all runs from Strava and MMF."""
    mmf_runs = [Run.from_mmf(mmf_run) for mmf_run in load_mmf_runs()]
    strava_runs = [
        Run.from_strava(strava_run) for strava_run in load_strava_runs(strava_client)
    ]
    return sorted(mmf_runs + strava_runs, key=lambda run: run.datetime_utc)
