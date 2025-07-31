"""Shoe management routes."""

from fastapi import APIRouter, HTTPException

from fitness.db.shoes import get_all_shoes, get_shoe_by_id, get_retired_shoes, get_active_shoes
from fitness.models.shoe import Shoe
from fitness.services.retirement import RetirementService
from .models import RetireShoeRequest, UpdateShoeRequest

router = APIRouter(prefix="/shoes", tags=["shoes"])


@router.get("/")
def read_shoes(retired: bool | None = None) -> list[Shoe]:
    """Get shoes, optionally filtered by retirement status.
    
    Args:
        retired: If True, return only retired shoes. If False, return only active shoes. 
                If None, return all shoes.
    """
    if retired is True:
        return get_retired_shoes()
    elif retired is False:
        return get_active_shoes()
    else:
        return get_all_shoes()



@router.patch("/{shoe_id}")
def update_shoe(shoe_id: str, request: UpdateShoeRequest) -> dict:
    """Update shoe properties. Use retired_at=null to unretire, or provide a date to retire."""
    # First check if shoe exists
    shoe = get_shoe_by_id(shoe_id)
    if not shoe:
        raise HTTPException(status_code=404, detail=f"Shoe with ID '{shoe_id}' not found")
    
    retirement_service = RetirementService()
    
    if request.retired_at is None:
        # Unretire the shoe
        retirement_service.unretire_shoe_by_id(shoe_id)
        return {"message": f"Shoe '{shoe.name}' has been unretired"}
    else:
        # Retire the shoe
        success = retirement_service.retire_shoe_by_id(
            shoe_id=shoe_id,
            retired_at=request.retired_at,
            retirement_notes=request.retirement_notes,
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Shoe with ID '{shoe_id}' not found")
        return {"message": f"Shoe '{shoe.name}' has been retired"}