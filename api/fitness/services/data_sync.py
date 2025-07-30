"""Data synchronization service to load external data into the database."""

from typing import List
from datetime import datetime

from fitness.models import Run
from fitness.models.database import RunCreate
from fitness.services.run_service import RunService
from fitness.load import load_all_runs
from fitness.load.strava.client import StravaClient


class DataSyncService:
    """Service for synchronizing external data sources with the database."""
    
    def __init__(self, run_service: RunService):
        self.run_service = run_service
    
    def convert_run_to_create(self, run: Run) -> RunCreate:
        """Convert a Pydantic Run model to a RunCreate model for database insertion."""
        return RunCreate(
            datetime_utc=run.datetime_utc,
            type=run.type,
            distance=run.distance,
            duration=run.duration,
            source=run.source,
            avg_heart_rate=run.avg_heart_rate,
            shoes=run.shoes,
        )
    
    def sync_all_runs_from_sources(self, strava_client: StravaClient | None = None) -> dict:
        """
        Load all runs from external sources and sync with database.
        
        Returns a summary of the sync operation.
        """
        # Load runs from external sources
        external_runs = load_all_runs(strava_client)
        
        # Convert to database models
        run_creates = [self.convert_run_to_create(run) for run in external_runs]
        
        # Clear existing data (for now - in future we might want to be smarter about this)
        cleared_count = self.run_service.clear_all_runs()
        
        # Bulk insert new data
        created_runs = self.run_service.bulk_create_runs(run_creates)
        
        return {
            "status": "success",
            "cleared_runs": cleared_count,
            "loaded_runs": len(created_runs),
            "sources_synced": ["MapMyFitness", "Strava"],
            "synced_at": datetime.utcnow().isoformat(),
        }
    
    def sync_incremental(self, strava_client: StravaClient | None = None) -> dict:
        """
        Perform incremental sync (future enhancement).
        
        For now, this just calls sync_all_runs_from_sources but in the future
        we could implement smarter logic to only sync new/changed runs.
        """
        # TODO: Implement incremental sync logic
        # This could check timestamps, compare with existing data, etc.
        return self.sync_all_runs_from_sources(strava_client)