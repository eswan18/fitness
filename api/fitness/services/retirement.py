"""Service for managing shoe retirement status."""

from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel
from fitness.db.shoes import (
    get_shoe_by_name,
    retire_shoe as db_retire_shoe,
    unretire_shoe as db_unretire_shoe,
    get_retired_shoes,
    upsert_shoe,
)
from fitness.models.shoe import Shoe


class ShoeRetirementInfo(BaseModel):
    """Information about a retired shoe."""
    retired_at: date
    retirement_notes: Optional[str] = None

class RetirementService:
    """Service for managing shoe retirement status using database."""

    def __init__(self):
        """Initialize the retirement service.
        
        All retirement data is stored in the database.
        """
        pass

    def is_shoe_retired(self, shoe_name: str) -> bool:
        """Check if a shoe is retired."""
        shoe = get_shoe_by_name(shoe_name)
        if shoe is None:
            return False
        return shoe.is_retired

    def get_retirement_info(self, shoe_name: str) -> Optional[ShoeRetirementInfo]:
        """Get retirement information for a shoe."""
        shoe = get_shoe_by_name(shoe_name)
        if shoe is None or not shoe.is_retired or shoe.retired_at is None:
            return None
        return ShoeRetirementInfo(
            retired_at=shoe.retired_at,
            retirement_notes=shoe.retirement_notes,
        )

    def retire_shoe(
        self, shoe_name: str, retired_at: date, retirement_notes: Optional[str] = None
    ) -> None:
        """Retire a shoe."""
        # First ensure the shoe exists in database
        existing_shoe = get_shoe_by_name(shoe_name)
        if existing_shoe is None:
            # Create the shoe if it doesn't exist
            shoe = Shoe.retired_shoe(shoe_name, retired_at, retirement_notes)
            upsert_shoe(shoe)
        else:
            # Use the database retire function
            db_retire_shoe(shoe_name, retired_at, retirement_notes)

    def unretire_shoe(self, shoe_name: str) -> bool:
        """Unretire a shoe. Returns True if shoe was retired, False if it wasn't."""
        return db_unretire_shoe(shoe_name)

    def list_retired_shoes(self) -> Dict[str, ShoeRetirementInfo]:
        """List all retired shoes with their retirement information."""
        retired_shoes = get_retired_shoes()
        
        result = {}
        for shoe in retired_shoes:
            # Only include shoes that actually have a retirement date (should always be true for get_retired_shoes)
            if shoe.retired_at is not None:
                result[shoe.name] = ShoeRetirementInfo(
                    retired_at=shoe.retired_at,
                    retirement_notes=shoe.retirement_notes,
                )
        
        return result
