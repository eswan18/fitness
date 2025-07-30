from functools import cache
from typing import List

from sqlmodel import Session

from fitness.load.strava.client import StravaClient
from fitness.models import Run, RunRead
from fitness.database import get_session
from fitness.services.run_service import RunService
from fitness.services.data_sync import DataSyncService


@cache
def strava_client() -> StravaClient:
    """Get a cached Strava client instance that persists across requests."""
    return StravaClient.from_env()


def get_run_service(session: Session = None) -> RunService:
    """Get a RunService instance."""
    return RunService(session)


def all_runs(session: Session = None) -> List[Run]:
    """Get all runs from the database."""
    run_service = get_run_service(session)
    db_runs = run_service.get_runs(limit=10000)  # Get all runs
    
    # Convert RunRead models to Run models (now both are SQLModel-based)
    runs = [
        Run(
            datetime_utc=db_run.datetime_utc,
            type=db_run.type,
            distance=db_run.distance,
            duration=db_run.duration,
            source=db_run.source,
            avg_heart_rate=db_run.avg_heart_rate,
            shoes=db_run.shoes,
        )
        for db_run in db_runs
    ]
    
    return runs


def refresh_runs_data() -> List[Run]:
    """Refresh all runs data by syncing from external sources."""
    # Create services
    run_service = get_run_service()
    sync_service = DataSyncService(run_service)
    client = strava_client()
    
    # Sync data from external sources
    sync_result = sync_service.sync_all_runs_from_sources(client)
    
    # Return the updated runs
    return all_runs()
