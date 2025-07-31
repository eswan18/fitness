import logging
from datetime import date
from typing import List, Optional

from fitness.models.shoe import Shoe
from .connection import get_db_cursor

logger = logging.getLogger(__name__)


def create_shoe(shoe: Shoe) -> str:
    """Insert a new shoe into the database and return its ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO shoes (id, name, retired_at, notes, retirement_notes, deleted_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            shoe.id,
            shoe.name,
            shoe.retired_at,
            shoe.notes,
            shoe.retirement_notes,
            shoe.deleted_at
        ))
        return shoe.id


def get_all_shoes(include_deleted: bool = False) -> List[Shoe]:
    """Get all shoes from the database."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                ORDER BY name
            """)
        else:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE deleted_at IS NULL
                ORDER BY name
            """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def get_shoe_by_id(shoe_id: str, include_deleted: bool = False) -> Optional[Shoe]:
    """Get a specific shoe by its ID."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE id = %s
            """, (shoe_id,))
        else:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE id = %s AND deleted_at IS NULL
            """, (shoe_id,))
        row = cursor.fetchone()
        return _row_to_shoe(row) if row else None


def get_shoe_by_name(name: str, include_deleted: bool = False) -> Optional[Shoe]:
    """Get a specific shoe by its name."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE name = %s
            """, (name,))
        else:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE name = %s AND deleted_at IS NULL
            """, (name,))
        row = cursor.fetchone()
        return _row_to_shoe(row) if row else None


def get_retired_shoes(include_deleted: bool = False) -> List[Shoe]:
    """Get all retired shoes (shoes with retired_at set)."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE retired_at IS NOT NULL
                ORDER BY retired_at DESC
            """)
        else:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE retired_at IS NOT NULL AND deleted_at IS NULL
                ORDER BY retired_at DESC
            """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def get_active_shoes(include_deleted: bool = False) -> List[Shoe]:
    """Get all active (non-retired) shoes."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE retired_at IS NULL
                ORDER BY name
            """)
        else:
            cursor.execute("""
                SELECT id, name, retired_at, notes, retirement_notes, deleted_at
                FROM shoes
                WHERE retired_at IS NULL AND deleted_at IS NULL
                ORDER BY name
            """)
        rows = cursor.fetchall()
        return [_row_to_shoe(row) for row in rows]


def shoe_exists(shoe_name: str, include_deleted: bool = False) -> bool:
    """Check if a shoe with the given name exists."""
    with get_db_cursor() as cursor:
        if include_deleted:
            cursor.execute("""
                SELECT 1 FROM shoes
                WHERE name = %s
                LIMIT 1
            """, (shoe_name,))
        else:
            cursor.execute("""
                SELECT 1 FROM shoes
                WHERE name = %s AND deleted_at IS NULL
                LIMIT 1
            """, (shoe_name,))
        return cursor.fetchone() is not None


def upsert_shoe(shoe: Shoe) -> str:
    """Insert or update a shoe. Returns the shoe ID."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO shoes (id, name, retired_at, notes, retirement_notes, deleted_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                retired_at = EXCLUDED.retired_at,
                notes = EXCLUDED.notes,
                retirement_notes = EXCLUDED.retirement_notes,
                deleted_at = EXCLUDED.deleted_at,
                updated_at = CURRENT_TIMESTAMP
        """, (
            shoe.id,
            shoe.name,
            shoe.retired_at,
            shoe.notes,
            shoe.retirement_notes,
            shoe.deleted_at
        ))
        return shoe.id


def retire_shoe(name: str, retired_at: date, retirement_notes: Optional[str] = None) -> bool:
    """Retire a shoe by name. Returns True if shoe was found and retired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired_at = %s, retirement_notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND deleted_at IS NULL
        """, (retired_at, retirement_notes, name))
        return cursor.rowcount > 0


def unretire_shoe(name: str) -> bool:
    """Unretire a shoe by name. Returns True if shoe was found and unretired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired_at = NULL, retirement_notes = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND deleted_at IS NULL
        """, (name,))
        return cursor.rowcount > 0


def retire_shoe_by_id(shoe_id: str, retired_at: date, retirement_notes: Optional[str] = None) -> bool:
    """Retire a shoe by ID. Returns True if shoe was found and retired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired_at = %s, retirement_notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NULL
        """, (retired_at, retirement_notes, shoe_id))
        return cursor.rowcount > 0


def unretire_shoe_by_id(shoe_id: str) -> bool:
    """Unretire a shoe by ID. Returns True if shoe was found and unretired."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET retired_at = NULL, retirement_notes = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND deleted_at IS NULL
        """, (shoe_id,))
        return cursor.rowcount > 0


def soft_delete_shoe(name: str) -> bool:
    """Soft delete a shoe by name. Returns True if shoe was found and deleted."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND deleted_at IS NULL
        """, (name,))
        return cursor.rowcount > 0


def restore_shoe(name: str) -> bool:
    """Restore a soft-deleted shoe by name. Returns True if shoe was found and restored."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE shoes 
            SET deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND deleted_at IS NOT NULL
        """, (name,))
        return cursor.rowcount > 0


def delete_shoe(name: str) -> bool:
    """Hard delete a shoe by name. Returns True if shoe was found and deleted."""
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM shoes WHERE name = %s", (name,))
        return cursor.rowcount > 0


def _row_to_shoe(row) -> Shoe:
    """Convert a database row to a Shoe object."""
    shoe_id, name, retired_at, notes, retirement_notes, deleted_at = row
    return Shoe(
        id=shoe_id,
        name=name,
        retired_at=retired_at,
        notes=notes,
        retirement_notes=retirement_notes,
        deleted_at=deleted_at,
    )


def get_existing_shoes_by_names(shoe_names: set[str]) -> dict[str, str]:
    """Get existing shoes by their names. Returns dict mapping shoe_name -> shoe_id."""
    if not shoe_names:
        return {}
    
    logger.debug(f"Checking existence of {len(shoe_names)} shoes: {shoe_names}")
    
    with get_db_cursor() as cursor:
        # Create placeholders for IN clause
        placeholders = ','.join(['%s'] * len(shoe_names))
        cursor.execute(f"""
            SELECT name, id FROM shoes 
            WHERE name IN ({placeholders}) AND deleted_at IS NULL
        """, list(shoe_names))
        
        result = {name: shoe_id for name, shoe_id in cursor.fetchall()}
        logger.debug(f"Found {len(result)} existing shoes in database")
        return result


def bulk_create_shoes_by_names(shoe_names: set[str]) -> dict[str, str]:
    """Create multiple shoes by names. Returns dict mapping shoe_name -> shoe_id."""
    if not shoe_names:
        return {}
    
    logger.info(f"Creating {len(shoe_names)} new shoes: {shoe_names}")
    
    from fitness.models.shoe import generate_shoe_id
    
    # Generate shoe data
    shoe_data = [(generate_shoe_id(name), name) for name in shoe_names]
    
    with get_db_cursor() as cursor:
        cursor.executemany("""
            INSERT INTO shoes (id, name, retired_at, notes, retirement_notes, deleted_at)
            VALUES (%s, %s, NULL, NULL, NULL, NULL)
        """, shoe_data)
        
        logger.info(f"Successfully created {len(shoe_data)} shoes")
        
        # Return mapping of name -> id
        return {name: shoe_id for shoe_id, name in shoe_data} 