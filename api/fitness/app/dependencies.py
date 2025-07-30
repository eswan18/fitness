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
    from fitness.db.runs import delete_runs_by_source, bulk_create_runs

    # Get fresh data from external sources
    client = strava_client()
    fresh_runs = load_all_runs(client)

    # Clear existing data and insert fresh data
    # Note: This is a simple approach. In production, you might want more sophisticated
    # sync logic to avoid losing data or handle duplicates better

    # Group runs by source for efficient deletion/insertion
    mmf_runs = [run for run in fresh_runs if run.source == "MapMyFitness"]
    strava_runs = [run for run in fresh_runs if run.source == "Strava"]

    # Delete and re-insert MMF runs
    if mmf_runs:
        delete_runs_by_source("MapMyFitness")
        bulk_create_runs(mmf_runs)

    # Delete and re-insert Strava runs
    if strava_runs:
        delete_runs_by_source("Strava")
        bulk_create_runs(strava_runs)

    return all_runs()
