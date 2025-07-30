import logging
from datetime import date
from typing import List, Optional

from fitness.models import Run
from fitness.models.shoe import generate_shoe_id
from .connection import get_db_cursor

logger = logging.getLogger(__name__)


def _ensure_shoe_exists(shoe_name: str | None) -> str | None:
    """Ensure a shoe exists in the database and return its ID."""
    if shoe_name is None:
        return None
    
    shoe_id = generate_shoe_id(shoe_name)
    
    with get_db_cursor() as cursor:
        logger.debug(f"Checking if shoe {shoe_name} (ID: {shoe_id}) exists")
        # Check if shoe already exists (including soft-deleted ones)
        cursor.execute("SELECT 1 FROM shoes WHERE id = %s", (shoe_id,))
        if cursor.fetchone() is None:
            # Create the shoe if it doesn't exist
            cursor.execute("""
                INSERT INTO shoes (id, name, retirement_date, notes, deleted_at)
                VALUES (%s, %s, NULL, NULL, NULL)
            """, (shoe_id, shoe_name))
            logger.info(f"Created new shoe: {shoe_name} (ID: {shoe_id})")
    
    return shoe_id


def create_run(run: Run) -> str:
    """Insert a new run into the database and return its ID."""
    # Ensure the shoe exists and get its ID
    shoe_id = _ensure_shoe_exists(run.shoe_name)
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoe_id, deleted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            run.id,
            run.datetime_utc,
            run.type,
            run.distance,
            run.duration,
            run.source,
            run.avg_heart_rate,
            shoe_id,
            run.deleted_at
        ))
        logger.info(f"Created run {run.id} ({run.source})")
        return run.id


def get_all_runs(include_deleted: bool = False) -> List[Run]:
    """Get all runs from the database with shoe information."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                ORDER BY r.datetime_utc
            """)
        else:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE r.deleted_at IS NULL
                ORDER BY r.datetime_utc
            """)
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def get_run_by_id(run_id: str, include_deleted: bool = False) -> Optional[Run]:
    """Get a specific run by its ID."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE r.id = %s
            """, (run_id,))
        else:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE r.id = %s AND r.deleted_at IS NULL
            """, (run_id,))
        row = cursor.fetchone()
        return _row_to_run(row) if row else None


def get_runs_in_date_range(start_date: date, end_date: date, include_deleted: bool = False) -> List[Run]:
    """Get runs within a specific date range (based on UTC dates)."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE DATE(r.datetime_utc) BETWEEN %s AND %s
                ORDER BY r.datetime_utc
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE DATE(r.datetime_utc) BETWEEN %s AND %s AND r.deleted_at IS NULL
                ORDER BY r.datetime_utc
            """, (start_date, end_date))
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def get_runs_by_source(source: str, include_deleted: bool = False) -> List[Run]:
    """Get all runs from a specific source."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE r.source = %s
                ORDER BY r.datetime_utc
            """, (source,))
        else:
            cursor.execute("""
                SELECT r.id, r.datetime_utc, r.type, r.distance, r.duration, r.source, r.avg_heart_rate, r.shoe_id, r.deleted_at, s.name
                FROM runs r
                LEFT JOIN shoes s ON r.shoe_id = s.id
                WHERE r.source = %s AND r.deleted_at IS NULL
                ORDER BY r.datetime_utc
            """, (source,))
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def soft_delete_runs_by_source(source: str) -> int:
    """Soft delete all runs from a specific source. Returns the number of deleted rows."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE runs 
            SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE source = %s AND deleted_at IS NULL
        """, (source,))
        return cursor.rowcount


def delete_runs_by_source(source: str) -> int:
    """Hard delete all runs from a specific source. Returns the number of deleted rows."""
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM runs WHERE source = %s", (source,))
        return cursor.rowcount


def soft_delete_run(run_id: str) -> bool:
    """Soft delete a run by ID. Returns True if run was found and deleted."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE runs 
            SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NULL
        """, (run_id,))
        return cursor.rowcount > 0


def restore_run(run_id: str) -> bool:
    """Restore a soft-deleted run by ID. Returns True if run was found and restored."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE runs 
            SET deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NOT NULL
        """, (run_id,))
        return cursor.rowcount > 0


def run_exists(run: Run, include_deleted: bool = False) -> bool:
    """Check if a run with the same ID already exists."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT 1 FROM runs
                WHERE id = %s
                LIMIT 1
            """, (run.id,))
        else:
            cursor.execute("""
                SELECT 1 FROM runs
                WHERE id = %s AND deleted_at IS NULL
                LIMIT 1
            """, (run.id,))
        return cursor.fetchone() is not None


def upsert_run(run: Run) -> str:
    """Insert or update a run. Returns the run ID."""
    # Ensure the shoe exists and get its ID
    shoe_id = _ensure_shoe_exists(run.shoe_name)
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoe_id, deleted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                datetime_utc = EXCLUDED.datetime_utc,
                type = EXCLUDED.type,
                distance = EXCLUDED.distance,
                duration = EXCLUDED.duration,
                source = EXCLUDED.source,
                avg_heart_rate = EXCLUDED.avg_heart_rate,
                shoe_id = EXCLUDED.shoe_id,
                deleted_at = EXCLUDED.deleted_at,
                updated_at = CURRENT_TIMESTAMP
        """, (
            run.id,
            run.datetime_utc,
            run.type,
            run.distance,
            run.duration,
            run.source,
            run.avg_heart_rate,
            shoe_id,
            run.deleted_at
        ))
        return run.id


def bulk_create_runs(runs: List[Run], chunk_size: int = 20) -> int:
    """Insert multiple runs into the database in chunks. Returns the number of inserted rows."""
    if not runs:
        return 0
    
    logger.info(f"Starting bulk insert of {len(runs)} runs in chunks of {chunk_size}")
    
    # Ensure all shoes exist first
    for run in runs:
        _ensure_shoe_exists(run.shoe_name)
    
    total_inserted = 0
    
    with get_db_cursor() as cursor:
        # Process runs in chunks
        for i in range(0, len(runs), chunk_size):
            chunk = runs[i:i + chunk_size]
            
            data = [
                (run.id, run.datetime_utc, run.type, run.distance, run.duration, 
                 run.source, run.avg_heart_rate, _ensure_shoe_exists(run.shoe_name), run.deleted_at)
                for run in chunk
            ]
            
            cursor.executemany("""
                INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoe_id, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
            
            chunk_inserted = cursor.rowcount
            total_inserted += chunk_inserted
            logger.info(f"Inserted {chunk_inserted} runs in chunk {i//chunk_size + 1} (runs {i+1}-{min(i+chunk_size, len(runs))})")
            
    logger.info(f"Bulk insert completed: {total_inserted} total runs inserted")
    return total_inserted


def bulk_upsert_runs(runs: List[Run], chunk_size: int = 20) -> int:
    """Insert or update multiple runs in the database in chunks. Returns the number of affected rows."""
    if not runs:
        return 0
    
    logger.info(f"Starting bulk upsert of {len(runs)} runs in chunks of {chunk_size}")
    
    # Ensure all shoes exist first
    for run in runs:
        _ensure_shoe_exists(run.shoe_name)
    
    total_affected = 0
    
    with get_db_cursor() as cursor:
        # Process runs in chunks
        for i in range(0, len(runs), chunk_size):
            chunk = runs[i:i + chunk_size]
            
            data = [
                (run.id, run.datetime_utc, run.type, run.distance, run.duration, 
                 run.source, run.avg_heart_rate, _ensure_shoe_exists(run.shoe_name), run.deleted_at)
                for run in chunk
            ]
            
            cursor.executemany("""
                INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoe_id, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    datetime_utc = EXCLUDED.datetime_utc,
                    type = EXCLUDED.type,
                    distance = EXCLUDED.distance,
                    duration = EXCLUDED.duration,
                    source = EXCLUDED.source,
                    avg_heart_rate = EXCLUDED.avg_heart_rate,
                    shoe_id = EXCLUDED.shoe_id,
                    deleted_at = EXCLUDED.deleted_at,
                    updated_at = CURRENT_TIMESTAMP
            """, data)
            
            chunk_affected = cursor.rowcount
            total_affected += chunk_affected
            logger.info(f"Upserted {chunk_affected} runs in chunk {i//chunk_size + 1} (runs {i+1}-{min(i+chunk_size, len(runs))})")
            
    logger.info(f"Bulk upsert completed: {total_affected} total runs affected")
    return total_affected


def get_existing_run_ids() -> set[str]:
    """Get all existing run IDs from the database."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id FROM runs WHERE deleted_at IS NULL")
        rows = cursor.fetchall()
        existing_ids = {row[0] for row in rows}
        logger.info(f"Found {len(existing_ids)} existing run IDs in database")
        return existing_ids


def _row_to_run(row) -> Run:
    """Convert a database row to a Run object."""
    run_id, datetime_utc, type_, distance, duration, source, avg_heart_rate, shoe_id, deleted_at, shoe_name = row
    run = Run(
        id=run_id,
        datetime_utc=datetime_utc,
        type=type_,
        distance=distance,
        duration=duration,
        source=source,
        avg_heart_rate=avg_heart_rate,
        shoe_id=shoe_id,
        deleted_at=deleted_at,
    )
    run._shoe_name = shoe_name
    return run
