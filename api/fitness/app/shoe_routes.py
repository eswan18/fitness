"""Shoe management routes."""

from fastapi import APIRouter, HTTPException

from fitness.db.shoes import get_all_shoes
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
    retirement_service = RetirementService()
    retired_shoes = retirement_service.list_retired_shoes()
    return [
        {
            "shoe": shoe_name,
            "retired_at": info.retired_at.isoformat(),
            "retirement_notes": info.retirement_notes,
        }
        for shoe_name, info in retired_shoes.items()
    ]


@router.post("/{shoe_name}/retire")
def retire_shoe(shoe_name: str, request: RetireShoeRequest) -> dict:
    """Retire a shoe."""
    retirement_service = RetirementService()
    retirement_service.retire_shoe(
        shoe_name=shoe_name,
        retired_at=request.retired_at,
        retirement_notes=request.retirement_notes,
    )
    return {"message": f"Shoe '{shoe_name}' has been retired"}


@router.delete("/{shoe_name}/retire")
def unretire_shoe(shoe_name: str) -> dict:
    """Unretire a shoe."""
    retirement_service = RetirementService()
    was_retired = retirement_service.unretire_shoe(shoe_name)
    if not was_retired:
        raise HTTPException(
            status_code=404, detail=f"Shoe '{shoe_name}' was not retired"
        )
    return {"message": f"Shoe '{shoe_name}' has been unretired"}