import logging

from fastapi import HTTPException

from fitness.integrations.strava.client import StravaClient
from fitness.models import Run
from fitness.db.runs import get_all_runs
from fitness.db.oauth_credentials import get_credentials

logger = logging.getLogger(__name__)


def _strava_client() -> StravaClient:
    """Get a Strava client instance.

    The client is initialized from environment variables and will connect
    lazily as needed.
    """
    strava_creds = get_credentials("strava")
    if strava_creds is None:
        raise HTTPException(
            status_code=500, detail="Strava credentials not found in database"
        )
    client = StravaClient(creds=strava_creds)
    return client


def all_runs() -> list[Run]:
    """Get all runs from the database."""
    return get_all_runs()


def update_new_runs_only() -> dict[str, int | list[str]]:
    """Fetch external data and insert only runs that don't exist in database.

    Returns a summary containing counts and the list of newly inserted run IDs.
    """
    from fitness.load import load_all_runs
    from fitness.db.runs import get_existing_run_ids, bulk_create_runs

    logger.info("Starting data update from external sources")

    try:
        # Get fresh data from external sources
        logger.info("Fetching runs from external sources (Strava + MMF)")
        client = _strava_client()
        all_external_runs = load_all_runs(client)
        logger.info(
            f"Successfully loaded {len(all_external_runs)} runs from external sources"
        )

        # Get existing run IDs from database
        logger.info("Querying existing run IDs from database")
        existing_ids = get_existing_run_ids()
        logger.info(f"Found {len(existing_ids)} existing runs in database")

        # Filter to only new runs
        new_runs = [run for run in all_external_runs if run.id not in existing_ids]
        logger.info(
            f"Filtered to {len(new_runs)} new runs "
            f"({len(all_external_runs) - len(new_runs)} already exist)"
        )

        # Insert only the new runs
        if new_runs:
            logger.info(f"Inserting {len(new_runs)} new runs into database")
            new_run_ids = [run.id for run in new_runs]
            logger.debug(f"New run IDs to insert: {new_run_ids}")
            inserted_count = bulk_create_runs(new_runs)
            logger.info(f"Successfully inserted {inserted_count} new runs")
        else:
            inserted_count = 0
            logger.info("No new runs to insert")

        result = {
            "total_external_runs": len(all_external_runs),
            "existing_in_db": len(existing_ids),
            "new_runs_found": len(new_runs),
            "new_runs_inserted": inserted_count,
            "new_run_ids": [run.id for run in new_runs],
        }

        logger.info(
            f"Data update completed successfully: "
            f"{result['new_runs_inserted']} new runs inserted"
        )

        return result

    except Exception as e:
        logger.error(
            f"Data update failed with error: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        raise
