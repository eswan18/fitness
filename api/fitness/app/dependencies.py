from fitness.load.strava.client import StravaClient
from fitness.models import Run
from fitness.db.runs import get_all_runs


def strava_client() -> StravaClient:
    """Get a Strava client instance."""
    return StravaClient.from_env()


def all_runs() -> list[Run]:
    """Get all runs from the database."""
    return get_all_runs()


def update_new_runs_only() -> dict[str, int | list[str]]:
    """Fetch external data and insert only runs that don't exist in database."""
    from fitness.load import load_all_runs
    from fitness.db.runs import get_existing_run_ids, bulk_create_runs

    # Get fresh data from external sources
    client = strava_client()
    all_external_runs = load_all_runs(client)

    # Get existing run IDs from database
    existing_ids = get_existing_run_ids()

    # Filter to only new runs
    new_runs = [run for run in all_external_runs if run.id not in existing_ids]

    # Insert only the new runs
    if new_runs:
        inserted_count = bulk_create_runs(new_runs)
    else:
        inserted_count = 0

    return {
        "total_external_runs": len(all_external_runs),
        "existing_in_db": len(existing_ids),
        "new_runs_found": len(new_runs),
        "new_runs_inserted": inserted_count,
        "new_run_ids": [run.id for run in new_runs],
    }
