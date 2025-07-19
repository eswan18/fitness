from functools import cache

from fitness.load import load_all_runs
from fitness.models import Run


@cache
def all_runs() -> list[Run]:
    return load_all_runs()


def clear_runs_cache() -> None:
    """Clear the cached runs data."""
    all_runs.cache_clear()


def refresh_runs_data() -> list[Run]:
    """Clear the cache and reload all runs data."""
    clear_runs_cache()
    return all_runs()
