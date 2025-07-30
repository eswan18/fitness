from __future__ import annotations
from datetime import date
from typing import Optional
import re

from pydantic import BaseModel


def generate_shoe_id(shoe_name: str) -> str:
    """
    Generate a deterministic ID from a shoe name.
    
    Normalizes the name by:
    - Converting to lowercase
    - Replacing spaces and special chars with underscores
    - Removing consecutive underscores
    - Stripping leading/trailing underscores
    """
    # Convert to lowercase and replace spaces/special chars with underscores
    normalized = re.sub(r'[^a-z0-9]+', '_', shoe_name.lower())
    # Remove consecutive underscores and strip
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    return normalized


class Shoe(BaseModel):
    id: str  # Generated from shoe name
    name: str  # The display name of the shoe
    retired: bool = False
    retirement_date: Optional[date] = None
    notes: Optional[str] = None

    @classmethod
    def from_name(cls, name: str) -> Shoe:
        """Create a new shoe from just a name."""
        return cls(
            id=generate_shoe_id(name),
            name=name,
        )

    @classmethod
    def retired_shoe(
        cls, 
        name: str, 
        retirement_date: date, 
        notes: Optional[str] = None
    ) -> Shoe:
        """Create a retired shoe."""
        return cls(
            id=generate_shoe_id(name),
            name=name,
            retired=True,
            retirement_date=retirement_date,
            notes=notes,
        )

    def retire(self, retirement_date: date, notes: Optional[str] = None) -> None:
        """Mark this shoe as retired."""
        self.retired = True
        self.retirement_date = retirement_date
        self.notes = notes

    def unretire(self) -> None:
        """Mark this shoe as active (not retired)."""
        self.retired = False
        self.retirement_date = None
        self.notes = None 