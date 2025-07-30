from fitness.load.strava.client import StravaClient
from fitness.models import Run
from fitness.db.runs import get_all_runs


def strava_client() -> StravaClient:
    """Get a Strava client instance."""
    return StravaClient.from_env()


def all_runs() -> list[Run]:
    """Get all runs from the database."""
    return get_all_runs()


def refresh_runs_data() -> list[Run]:
    """Refresh runs data from external sources and update the database."""
    from fitness.load import load_all_runs
    from fitness.db.runs import bulk_upsert_runs
    
    # Get fresh data from external sources
    client = strava_client()
    fresh_runs = load_all_runs(client)
    
    # Use upsert to handle both new runs and updates to existing ones
    # This is more graceful than delete/insert since we now have deterministic IDs
    bulk_upsert_runs(fresh_runs)
    
    return all_runs()
