"""
API endpoints for run editing and history management.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from fitness.db.runs import get_run_by_id
from fitness.db.runs_history import (
    update_run_with_history,
    get_run_history,
    get_run_version,
    RunHistoryRecord,
    create_original_history_entries
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs", tags=["run-editing"])


class RunUpdateRequest(BaseModel):
    """Request model for updating a run."""
    distance: Optional[float] = Field(None, ge=0, description="Distance in miles")
    duration: Optional[float] = Field(None, ge=0, description="Duration in seconds")  
    avg_heart_rate: Optional[float] = Field(None, ge=0, le=220, description="Average heart rate")
    type: Optional[str] = Field(None, pattern="^(Outdoor Run|Treadmill Run)$", description="Run type")
    shoe_id: Optional[str] = Field(None, description="Shoe ID (foreign key)")
    datetime_utc: Optional[datetime] = Field(None, description="When the run occurred (UTC)")
    change_reason: Optional[str] = Field(None, description="Reason for the change")
    changed_by: str = Field(..., description="User making the change")


class RunHistoryResponse(BaseModel):
    """Response model for run history."""
    history_id: int
    run_id: str
    version_number: int
    change_type: str
    datetime_utc: datetime
    type: str
    distance: float
    duration: float
    source: str
    avg_heart_rate: Optional[float]
    shoe_id: Optional[str]
    changed_at: datetime
    changed_by: Optional[str]
    change_reason: Optional[str]

    @classmethod
    def from_history_record(cls, record: RunHistoryRecord) -> "RunHistoryResponse":
        """Convert a RunHistoryRecord to a response model."""
        return cls(
            history_id=record.history_id,
            run_id=record.run_id,
            version_number=record.version_number,
            change_type=record.change_type,
            datetime_utc=record.datetime_utc,
            type=record.type,
            distance=record.distance,
            duration=record.duration,
            source=record.source,
            avg_heart_rate=record.avg_heart_rate,
            shoe_id=record.shoe_id,
            changed_at=record.changed_at,
            changed_by=record.changed_by,
            change_reason=record.change_reason
        )


class BackfillStatusResponse(BaseModel):
    """Response model for backfill operations."""
    status: str
    records_processed: int
    message: str


@router.patch("/{run_id}")
def update_run(run_id: str, update_request: RunUpdateRequest) -> Dict[str, Any]:
    """
    Update a run with change tracking.
    
    This endpoint allows updating specific fields of a run while preserving
    the full edit history. The original state is saved before making changes.
    """
    try:
        # Verify the run exists
        existing_run = get_run_by_id(run_id)
        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run with ID {run_id} not found"
            )
        
        # Build updates dictionary, excluding None values
        updates = {}
        for field_name, field_value in update_request.model_dump().items():
            if field_name in ['changed_by', 'change_reason']:
                continue  # These are metadata, not run fields
            if field_value is not None:
                updates[field_name] = field_value
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        # Perform the update with history tracking
        update_run_with_history(
            run_id=run_id,
            updates=updates,
            changed_by=update_request.changed_by,
            change_reason=update_request.change_reason
        )
        
        logger.info(f"Successfully updated run {run_id} by {update_request.changed_by}")
        
        # Return the updated run
        updated_run = get_run_by_id(run_id)
        return {
            "status": "success",
            "message": f"Run {run_id} updated successfully",
            "run": updated_run.model_dump() if updated_run else None,
            "updated_fields": list(updates.keys()),
            "updated_at": datetime.now().isoformat(),
            "updated_by": update_request.changed_by
        }
        
    except ValueError as e:
        logger.error(f"Validation error updating run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is (like 404s)
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating run"
        )


@router.get("/{run_id}/history")
def get_run_edit_history(run_id: str, limit: Optional[int] = 50) -> List[RunHistoryResponse]:
    """
    Get the edit history for a specific run.
    
    Returns all historical versions of the run, ordered by version number (newest first).
    The first entry will be the most recent version, and the last will be the original.
    """
    try:
        # Verify the run exists
        existing_run = get_run_by_id(run_id)
        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run with ID {run_id} not found"
            )
        
        history_records = get_run_history(run_id, limit=limit)
        
        if not history_records:
            # Run exists but has no history - this could happen during migration
            logger.warning(f"Run {run_id} exists but has no history records")
            return []
        
        response = [RunHistoryResponse.from_history_record(record) for record in history_records]
        
        logger.debug(f"Retrieved {len(response)} history records for run {run_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is (like 404s)
        raise
    except Exception as e:
        logger.error(f"Error retrieving history for run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving run history"
        )


@router.get("/{run_id}/history/{version_number}")
def get_run_specific_version(run_id: str, version_number: int) -> RunHistoryResponse:
    """
    Get a specific version of a run from its history.
    
    This allows you to see exactly what the run looked like at a particular point in time.
    """
    try:
        # Verify the run exists
        existing_run = get_run_by_id(run_id)
        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run with ID {run_id} not found"
            )
        
        history_record = get_run_version(run_id, version_number)
        
        if not history_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found for run {run_id}"
            )
        
        return RunHistoryResponse.from_history_record(history_record)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error retrieving version {version_number} for run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving run version"
        )


@router.post("/history/backfill")
def backfill_original_history(batch_size: int = 1000) -> BackfillStatusResponse:
    """
    Create 'original' history entries for existing runs.
    
    This endpoint is used during the migration process to populate history
    for runs that existed before the edit tracking feature was implemented.
    
    **Note**: This should typically only be run once during the initial setup.
    """
    try:
        if batch_size <= 0 or batch_size > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size must be between 1 and 5000"
            )
        
        records_processed = create_original_history_entries(batch_size)
        
        if records_processed > 0:
            message = f"Successfully created original history entries for {records_processed} runs"
            status_value = "success"
        else:
            message = "No runs found that need original history entries"
            status_value = "no_action_needed"
        
        logger.info(f"Backfill completed: {message}")
        
        return BackfillStatusResponse(
            status=status_value,
            records_processed=records_processed,
            message=message
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error during history backfill: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during backfill process"
        )


# TODO: Add restore endpoint
@router.post("/{run_id}/restore/{version_number}")
def restore_run_to_version(run_id: str, version_number: int, restored_by: str) -> Dict[str, Any]:
    """
    Restore a run to a previous version.
    
    This creates a new version that copies the data from the specified historical version.
    The original version being restored to is preserved in the history.
    """
    try:
        # Verify the run exists
        existing_run = get_run_by_id(run_id)
        if not existing_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run with ID {run_id} not found"
            )
        
        # Get the historical version to restore to
        historical_version = get_run_version(run_id, version_number)
        if not historical_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found for run {run_id}"
            )
        
        # Build updates from the historical version
        # Only include fields that can be updated (not source, etc.)
        updates = {
            'distance': historical_version.distance,
            'duration': historical_version.duration,
            'type': historical_version.type,
            'avg_heart_rate': historical_version.avg_heart_rate,
            'shoe_id': historical_version.shoe_id,
            'datetime_utc': historical_version.datetime_utc
        }
        
        # Perform the restoration with history tracking
        update_run_with_history(
            run_id=run_id,
            updates=updates,
            changed_by=restored_by,
            change_reason=f"Restored to version {version_number}"
        )
        
        logger.info(f"Successfully restored run {run_id} to version {version_number} by {restored_by}")
        
        # Return the updated run
        updated_run = get_run_by_id(run_id)
        return {
            "status": "success",
            "message": f"Run {run_id} restored to version {version_number}",
            "run": updated_run.model_dump() if updated_run else None,
            "restored_from_version": version_number,
            "restored_at": datetime.now().isoformat(),
            "restored_by": restored_by
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error restoring run {run_id} to version {version_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during restoration"
        )