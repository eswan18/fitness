"""Shoe management routes."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict

from fitness.db.shoes import (
    get_shoes,
    get_shoe_by_id,
    retire_shoe_by_id,
    unretire_shoe_by_id,
)
from fitness.models.shoe import Shoe
from .models import UpdateShoeRequest

router = APIRouter(prefix="/shoes", tags=["shoes"])


@router.get("/", response_model=List[Shoe])
def read_shoes(retired: bool | None = None) -> list[Shoe]:
    """Get shoes, optionally filtered by retirement status.

    Args:
        retired: If True, return only retired shoes. If False, return only active shoes.
                If None, return all shoes.
    """
    return get_shoes(retired=retired)


@router.patch("/{shoe_id}", response_model=Dict[str, str])
def update_shoe(shoe_id: str, request: UpdateShoeRequest) -> dict:
    """Update shoe properties. Use retired_at=null to unretire, or provide a date to retire."""
    # First check if shoe exists
    shoe = get_shoe_by_id(shoe_id)
    if not shoe:
        raise HTTPException(
            status_code=404, detail=f"Shoe with ID '{shoe_id}' not found"
        )

    if request.retired_at is None:
        # Unretire the shoe
        unretire_shoe_by_id(shoe_id)
        return {"message": f"Shoe '{shoe.name}' has been unretired"}
    else:
        # Retire the shoe
        success = retire_shoe_by_id(
            shoe_id=shoe_id,
            retired_at=request.retired_at,
            retirement_notes=request.retirement_notes,
        )
        if not success:
            raise HTTPException(
                status_code=404, detail=f"Shoe with ID '{shoe_id}' not found"
            )
        return {"message": f"Shoe '{shoe.name}' has been retired"}
