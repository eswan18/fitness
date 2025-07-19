from functools import cache

from fitness.load import load_all_runs
from fitness.load.strava.client import StravaClient
from fitness.models import Run


@cache
def strava_client() -> StravaClient:
    """Get a cached Strava client instance that persists across requests."""
    return StravaClient.from_env()


@cache
def all_runs() -> list[Run]:
    client = strava_client()
    return load_all_runs(client)


def clear_runs_cache() -> None:
    """Clear the cached runs data."""
    all_runs.cache_clear()


def refresh_runs_data() -> list[Run]:
    """Clear the cache and reload all runs data."""
    clear_runs_cache()
    return all_runs()
