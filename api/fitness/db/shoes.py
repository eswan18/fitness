from datetime import date
from typing import List, Optional

from fitness.models.shoe import Shoe
from .connection import get_db_cursor


def create_shoe(shoe: Shoe) -> str:
    """Insert a new shoe into the database and return its ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO shoes (id, name, retired, retirement_date, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            shoe.id,
            shoe.name,
            shoe.retired,
            shoe.retirement_date,
            shoe.notes
        ))
        return shoe.id


def get_all_shoes() -> List[Shoe]:
    """Get all shoes from the database."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, retired, retirement_date, notes
            FROM shoes
            ORDER BY name
        """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def get_shoe_by_id(shoe_id: str) -> Optional[Shoe]:
    """Get a specific shoe by its ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, retired, retirement_date, notes
            FROM shoes
            WHERE id = %s
        """, (shoe_id,))
        row = cursor.fetchone()
        return _row_to_shoe(row) if row else None


def get_shoe_by_name(name: str) -> Optional[Shoe]:
    """Get a specific shoe by its name."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, retired, retirement_date, notes
            FROM shoes
            WHERE name = %s
        """, (name,))
        row = cursor.fetchone()
        return _row_to_shoe(row) if row else None


def get_retired_shoes() -> List[Shoe]:
    """Get all retired shoes."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, retired, retirement_date, notes
            FROM shoes
            WHERE retired = TRUE
            ORDER BY retirement_date DESC
        """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def get_active_shoes() -> List[Shoe]:
    """Get all active (non-retired) shoes."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, retired, retirement_date, notes
            FROM shoes
            WHERE retired = FALSE
            ORDER BY name
        """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def shoe_exists(shoe_name: str) -> bool:
    """Check if a shoe with the given name exists."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM shoes
            WHERE name = %s
            LIMIT 1
        """, (shoe_name,))
        return cursor.fetchone() is not None


def upsert_shoe(shoe: Shoe) -> str:
    """Insert or update a shoe. Returns the shoe ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO shoes (id, name, retired, retirement_date, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                retired = EXCLUDED.retired,
                retirement_date = EXCLUDED.retirement_date,
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            shoe.id,
            shoe.name,
            shoe.retired,
            shoe.retirement_date,
            shoe.notes
        ))
        return shoe.id


def retire_shoe(name: str, retirement_date: date, notes: Optional[str] = None) -> bool:
    """Retire a shoe by name. Returns True if shoe was found and retired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired = TRUE, retirement_date = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s
        """, (retirement_date, notes, name))
        return cursor.rowcount > 0


def unretire_shoe(name: str) -> bool:
    """Unretire a shoe by name. Returns True if shoe was found and unretired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired = FALSE, retirement_date = NULL, notes = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s
        """, (name,))
        return cursor.rowcount > 0


def delete_shoe(name: str) -> bool:
    """Delete a shoe by name. Returns True if shoe was found and deleted."""
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM shoes WHERE name = %s", (name,))
        return cursor.rowcount > 0


def _row_to_shoe(row) -> Shoe:
    """Convert a database row to a Shoe object."""
    shoe_id, name, retired, retirement_date, notes = row
    return Shoe(
        id=shoe_id,
        name=name,
        retired=retired,
        retirement_date=retirement_date,
        notes=notes
    ) 