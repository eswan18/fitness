from datetime import date
from typing import List, Optional

from fitness.models import Run
from .connection import get_db_cursor


def create_run(run: Run) -> str:
    """Insert a new run into the database and return its ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            run.id,
            run.datetime_utc,
            run.type,
            run.distance,
            run.duration,
            run.source,
            run.avg_heart_rate,
            run.shoes
        ))
        return run.id


def get_all_runs() -> List[Run]:
    """Get all runs from the database."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes
            FROM runs
            ORDER BY datetime_utc
        """)
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def get_run_by_id(run_id: str) -> Optional[Run]:
    """Get a specific run by its ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes
            FROM runs
            WHERE id = %s
        """, (run_id,))
        row = cursor.fetchone()
        return _row_to_run(row) if row else None


def get_runs_in_date_range(start_date: date, end_date: date) -> List[Run]:
    """Get runs within a specific date range (based on UTC dates)."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes
            FROM runs
            WHERE DATE(datetime_utc) BETWEEN %s AND %s
            ORDER BY datetime_utc
        """, (start_date, end_date))
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def get_runs_by_source(source: str) -> List[Run]:
    """Get all runs from a specific source."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes
            FROM runs
            WHERE source = %s
            ORDER BY datetime_utc
        """, (source,))
        rows = cursor.fetchall()
        return [_row_to_run(row) for row in rows]


def delete_runs_by_source(source: str) -> int:
    """Delete all runs from a specific source. Returns the number of deleted rows."""
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM runs WHERE source = %s", (source,))
        return cursor.rowcount


def run_exists(run: Run) -> bool:
    """Check if a run with the same ID already exists."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM runs
            WHERE id = %s
            LIMIT 1
        """, (run.id,))
        return cursor.fetchone() is not None


def upsert_run(run: Run) -> str:
    """Insert or update a run. Returns the run ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                datetime_utc = EXCLUDED.datetime_utc,
                type = EXCLUDED.type,
                distance = EXCLUDED.distance,
                duration = EXCLUDED.duration,
                source = EXCLUDED.source,
                avg_heart_rate = EXCLUDED.avg_heart_rate,
                shoes = EXCLUDED.shoes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            run.id,
            run.datetime_utc,
            run.type,
            run.distance,
            run.duration,
            run.source,
            run.avg_heart_rate,
            run.shoes
        ))
        return run.id


def bulk_create_runs(runs: List[Run]) -> int:
    """Insert multiple runs into the database. Returns the number of inserted rows."""
    if not runs:
        return 0
    
    with get_db_cursor() as cursor:
        # Use execute_batch for better performance with multiple inserts
        data = [
            (run.id, run.datetime_utc, run.type, run.distance, run.duration, 
             run.source, run.avg_heart_rate, run.shoes)
            for run in runs
        ]
        
        cursor.executemany("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        
        return cursor.rowcount


def bulk_upsert_runs(runs: List[Run]) -> int:
    """Insert or update multiple runs in the database. Returns the number of affected rows."""
    if not runs:
        return 0
    
    with get_db_cursor() as cursor:
        data = [
            (run.id, run.datetime_utc, run.type, run.distance, run.duration, 
             run.source, run.avg_heart_rate, run.shoes)
            for run in runs
        ]
        
        cursor.executemany("""
            INSERT INTO runs (id, datetime_utc, type, distance, duration, source, avg_heart_rate, shoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                datetime_utc = EXCLUDED.datetime_utc,
                type = EXCLUDED.type,
                distance = EXCLUDED.distance,
                duration = EXCLUDED.duration,
                source = EXCLUDED.source,
                avg_heart_rate = EXCLUDED.avg_heart_rate,
                shoes = EXCLUDED.shoes,
                updated_at = CURRENT_TIMESTAMP
        """, data)
        
        return cursor.rowcount


def _row_to_run(row) -> Run:
    """Convert a database row to a Run object."""
    run_id, datetime_utc, type_, distance, duration, source, avg_heart_rate, shoes = row
    return Run(
        id=run_id,
        datetime_utc=datetime_utc,
        type=type_,
        distance=distance,
        duration=duration,
        source=source,
        avg_heart_rate=avg_heart_rate,
        shoes=shoes
    )
