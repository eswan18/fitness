"""Shoe management routes."""

from fastapi import APIRouter, HTTPException

from fitness.db.shoes import get_all_shoes, get_shoe_by_id
from fitness.models.shoe import Shoe
from fitness.services.retirement import RetirementService
from .models import RetireShoeRequest

router = APIRouter(prefix="/shoes", tags=["shoes"])


@router.get("/")
def list_all_shoes() -> list[Shoe]:
    """Get all shoes."""
    return get_all_shoes()


@router.get("/retired")
def list_retired_shoes() -> list[dict]:
    """Get all retired shoes."""
    from fitness.db.shoes import get_retired_shoes
    
    retired_shoes = get_retired_shoes()
    return [
        {
            "id": shoe.id,
            "name": shoe.name,
            "retired_at": shoe.retired_at.isoformat(),
            "retirement_notes": shoe.retirement_notes,
        }
        for shoe in retired_shoes
        if shoe.retired_at is not None  # Safety check
    ]


@router.post("/{shoe_id}/retire")
def retire_shoe(shoe_id: str, request: RetireShoeRequest) -> dict:
    """Retire a shoe."""
    retirement_service = RetirementService()
    success = retirement_service.retire_shoe_by_id(
        shoe_id=shoe_id,
        retired_at=request.retired_at,
        retirement_notes=request.retirement_notes,
    )
    if not success:
        raise HTTPException(status_code=404, detail=f"Shoe with ID '{shoe_id}' not found")
    
    # Get shoe name for response message
    shoe = get_shoe_by_id(shoe_id)
    shoe_name = shoe.name if shoe else shoe_id
    return {"message": f"Shoe '{shoe_name}' has been retired"}


@router.delete("/{shoe_id}/retire")
def unretire_shoe(shoe_id: str) -> dict:
    """Unretire a shoe."""
    retirement_service = RetirementService()
    was_retired = retirement_service.unretire_shoe_by_id(shoe_id)
    if not was_retired:
        raise HTTPException(
            status_code=404, detail=f"Shoe with ID '{shoe_id}' was not retired or not found"
        )
    
    # Get shoe name for response message
    shoe = get_shoe_by_id(shoe_id)
    shoe_name = shoe.name if shoe else shoe_id
    return {"message": f"Shoe '{shoe_name}' has been unretired"}