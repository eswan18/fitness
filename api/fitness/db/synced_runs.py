"""Database access functions for synced runs (Google Calendar sync tracking)."""

import logging
from datetime import datetime
from typing import List, Optional

from fitness.models.sync import SyncedRun, SyncStatus
from .connection import get_db_cursor

logger = logging.getLogger(__name__)


def get_synced_run(run_id: str) -> Optional[SyncedRun]:
    """Get sync record for a specific run."""
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, run_id, run_version, google_event_id, synced_at, 
                   sync_status, error_message, created_at, updated_at
            FROM synced_runs
            WHERE run_id = %s
        """,
            (run_id,),
        )

        row = cursor.fetchone()
        if row is None:
            return None

        return SyncedRun(
            id=row[0],
            run_id=row[1],
            run_version=row[2],
            google_event_id=row[3],
            synced_at=row[4],
            sync_status=row[5],
            error_message=row[6],
            created_at=row[7],
            updated_at=row[8],
        )


def create_synced_run(
    run_id: str,
    google_event_id: str,
    run_version: int = 1,
    sync_status: SyncStatus = "synced",
    error_message: Optional[str] = None,
) -> SyncedRun:
    """Create a new sync record for a run."""
    with get_db_cursor() as cursor:
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO synced_runs 
            (run_id, run_version, google_event_id, synced_at, sync_status, error_message, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at, updated_at
        """,
            (
                run_id,
                run_version,
                google_event_id,
                now,
                sync_status,
                error_message,
                now,
                now,
            ),
        )

        result = cursor.fetchone()
        sync_id, created_at, updated_at = result

        logger.info(
            f"Created sync record for run {run_id} with Google event {google_event_id}"
        )

        return SyncedRun(
            id=sync_id,
            run_id=run_id,
            run_version=run_version,
            google_event_id=google_event_id,
            synced_at=now,
            sync_status=sync_status,
            error_message=error_message,
            created_at=created_at,
            updated_at=updated_at,
        )


def update_synced_run(
    run_id: str,
    run_version: Optional[int] = None,
    google_event_id: Optional[str] = None,
    sync_status: Optional[SyncStatus] = None,
    error_message: Optional[str] = None,
    clear_error_message: bool = False,
) -> Optional[SyncedRun]:
    """Update an existing sync record."""
    with get_db_cursor() as cursor:
        # Build dynamic UPDATE query based on provided fields
        update_fields = []
        params = []

        if run_version is not None:
            update_fields.append("run_version = %s")
            params.append(run_version)

        if google_event_id is not None:
            update_fields.append("google_event_id = %s")
            params.append(google_event_id)

        if sync_status is not None:
            update_fields.append("sync_status = %s")
            params.append(sync_status)

        if error_message is not None:
            update_fields.append("error_message = %s")
            params.append(error_message)
        elif clear_error_message:
            update_fields.append("error_message = NULL")
            # No parameter needed for NULL

        if not update_fields:
            # Nothing to update
            return get_synced_run(run_id)

        # Always update the updated_at timestamp
        update_fields.append("updated_at = %s")
        params.append(datetime.now())

        # Add run_id for WHERE clause
        params.append(run_id)

        query = f"""
            UPDATE synced_runs 
            SET {", ".join(update_fields)}
            WHERE run_id = %s
            RETURNING id, run_id, run_version, google_event_id, synced_at, 
                      sync_status, error_message, created_at, updated_at
        """

        cursor.execute(query, params)
        row = cursor.fetchone()

        if row is None:
            logger.warning(f"No sync record found for run {run_id} to update")
            return None

        logger.info(f"Updated sync record for run {run_id}")

        return SyncedRun(
            id=row[0],
            run_id=row[1],
            run_version=row[2],
            google_event_id=row[3],
            synced_at=row[4],
            sync_status=row[5],
            error_message=row[6],
            created_at=row[7],
            updated_at=row[8],
        )


def delete_synced_run(run_id: str) -> bool:
    """Delete a sync record for a run (when unsyncing from calendar)."""
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM synced_runs WHERE run_id = %s", (run_id,))
        deleted_count = cursor.rowcount

        if deleted_count > 0:
            logger.info(f"Deleted sync record for run {run_id}")
            return True
        else:
            logger.warning(f"No sync record found for run {run_id} to delete")
            return False


def get_all_synced_runs() -> List[SyncedRun]:
    """Get all sync records."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, run_id, run_version, google_event_id, synced_at, 
                   sync_status, error_message, created_at, updated_at
            FROM synced_runs
            ORDER BY synced_at DESC
        """)

        return [
            SyncedRun(
                id=row[0],
                run_id=row[1],
                run_version=row[2],
                google_event_id=row[3],
                synced_at=row[4],
                sync_status=row[5],
                error_message=row[6],
                created_at=row[7],
                updated_at=row[8],
            )
            for row in cursor.fetchall()
        ]


def is_run_synced(run_id: str) -> bool:
    """Check if a run is currently synced to Google Calendar."""
    synced_run = get_synced_run(run_id)
    return synced_run is not None and synced_run.sync_status == "synced"


def get_failed_syncs() -> List[SyncedRun]:
    """Get all runs with failed sync status for retry."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, run_id, run_version, google_event_id, synced_at, 
                   sync_status, error_message, created_at, updated_at
            FROM synced_runs
            WHERE sync_status = 'failed'
            ORDER BY updated_at DESC
        """)

        return [
            SyncedRun(
                id=row[0],
                run_id=row[1],
                run_version=row[2],
                google_event_id=row[3],
                synced_at=row[4],
                sync_status=row[5],
                error_message=row[6],
                created_at=row[7],
                updated_at=row[8],
            )
            for row in cursor.fetchall()
        ]
