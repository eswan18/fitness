"""Service layer for run-related database operations."""

from datetime import datetime, date
from typing import List, Optional

from sqlmodel import Session, select, and_

from fitness.models.database import RunTable, RunCreate, RunRead, RunUpdate
from fitness.database import get_session_context


class RunService:
    """Service class for run database operations."""

    def __init__(self, session: Optional[Session] = None):
        """Initialize the service with an optional session."""
        self._session = session

    def _get_session(self) -> Session:
        """Get the session, either provided or create a new one."""
        if self._session:
            return self._session
        return get_session_context()

    def create_run(self, run_data: RunCreate) -> RunRead:
        """Create a new run in the database."""
        with self._get_session() as session:
            # Create the database model
            db_run = RunTable(
                datetime_utc=run_data.datetime_utc,
                type=run_data.type,
                distance=run_data.distance,
                duration=run_data.duration,
                source=run_data.source,
                avg_heart_rate=run_data.avg_heart_rate,
                shoes=run_data.shoes,
            )
            
            session.add(db_run)
            session.commit()
            session.refresh(db_run)
            
            # Convert to read model
            return RunRead.model_validate(db_run)

    def get_run(self, run_id: int) -> Optional[RunRead]:
        """Get a run by ID."""
        with self._get_session() as session:
            db_run = session.get(RunTable, run_id)
            if db_run:
                return RunRead.model_validate(db_run)
            return None

    def get_runs(
        self,
        skip: int = 0,
        limit: int = 1000,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        source: Optional[str] = None,
        shoes: Optional[str] = None,
    ) -> List[RunRead]:
        """Get runs with optional filtering."""
        with self._get_session() as session:
            query = select(RunTable)
            
            # Apply filters
            filters = []
            if start_date:
                filters.append(RunTable.datetime_utc >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                filters.append(RunTable.datetime_utc <= datetime.combine(end_date, datetime.max.time()))
            if source:
                filters.append(RunTable.source == source)
            if shoes:
                filters.append(RunTable.shoes == shoes)
            
            if filters:
                query = query.where(and_(*filters))
            
            # Apply pagination and ordering
            query = query.order_by(RunTable.datetime_utc.desc()).offset(skip).limit(limit)
            
            runs = session.exec(query).all()
            return [RunRead.model_validate(run) for run in runs]

    def update_run(self, run_id: int, run_update: RunUpdate) -> Optional[RunRead]:
        """Update a run by ID."""
        with self._get_session() as session:
            db_run = session.get(RunTable, run_id)
            if not db_run:
                return None
            
            # Update only provided fields
            update_data = run_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_run, field, value)
            
            # Update the updated_at timestamp
            db_run.updated_at = datetime.utcnow()
            
            session.add(db_run)
            session.commit()
            session.refresh(db_run)
            
            return RunRead.model_validate(db_run)

    def delete_run(self, run_id: int) -> bool:
        """Delete a run by ID. Returns True if deleted, False if not found."""
        with self._get_session() as session:
            db_run = session.get(RunTable, run_id)
            if not db_run:
                return False
            
            session.delete(db_run)
            session.commit()
            return True

    def bulk_create_runs(self, runs_data: List[RunCreate]) -> List[RunRead]:
        """Create multiple runs in a single transaction."""
        with self._get_session() as session:
            db_runs = []
            for run_data in runs_data:
                db_run = RunTable(
                    datetime_utc=run_data.datetime_utc,
                    type=run_data.type,
                    distance=run_data.distance,
                    duration=run_data.duration,
                    source=run_data.source,
                    avg_heart_rate=run_data.avg_heart_rate,
                    shoes=run_data.shoes,
                )
                db_runs.append(db_run)
            
            session.add_all(db_runs)
            session.commit()
            
            # Refresh all objects to get their IDs
            for db_run in db_runs:
                session.refresh(db_run)
            
            return [RunRead.model_validate(run) for run in db_runs]

    def get_runs_count(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        source: Optional[str] = None,
        shoes: Optional[str] = None,
    ) -> int:
        """Get count of runs with optional filtering."""
        with self._get_session() as session:
            query = select(RunTable)
            
            # Apply same filters as get_runs
            filters = []
            if start_date:
                filters.append(RunTable.datetime_utc >= datetime.combine(start_date, datetime.min.time()))
            if end_date:
                filters.append(RunTable.datetime_utc <= datetime.combine(end_date, datetime.max.time()))
            if source:
                filters.append(RunTable.source == source)
            if shoes:
                filters.append(RunTable.shoes == shoes)
            
            if filters:
                query = query.where(and_(*filters))
            
            runs = session.exec(query).all()
            return len(runs)

    def clear_all_runs(self) -> int:
        """Delete all runs from the database. Returns count of deleted runs."""
        with self._get_session() as session:
            runs = session.exec(select(RunTable)).all()
            count = len(runs)
            
            for run in runs:
                session.delete(run)
            
            session.commit()
            return count