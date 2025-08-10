"""Google Calendar sync routes."""

from fastapi import APIRouter, HTTPException
from typing import List

from fitness.db.synced_runs import (
    get_synced_run,
    create_synced_run,
    update_synced_run,
    delete_synced_run,
    get_all_synced_runs,
    get_failed_syncs,
)
from fitness.models.sync import (
    SyncedRun,
    SyncResponse,
    SyncStatusResponse,
)

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/runs/{run_id}/status", response_model=SyncStatusResponse)
def get_sync_status(run_id: str) -> SyncStatusResponse:
    """Get the Google Calendar sync status for a specific run.

    Args:
        run_id: The ID of the run to check sync status for.

    Returns:
        SyncStatusResponse with current sync status information.
    """
    synced_run = get_synced_run(run_id)

    if synced_run is None:
        return SyncStatusResponse(
            run_id=run_id,
            is_synced=False,
            sync_status=None,
            synced_at=None,
            google_event_id=None,
            run_version=None,
            error_message=None,
        )

    return SyncStatusResponse(
        run_id=run_id,
        is_synced=synced_run.sync_status == "synced",
        sync_status=synced_run.sync_status,
        synced_at=synced_run.synced_at,
        google_event_id=synced_run.google_event_id,
        run_version=synced_run.run_version,
        error_message=synced_run.error_message,
    )


@router.post("/runs/{run_id}", response_model=SyncResponse)
def sync_run_to_calendar(run_id: str) -> SyncResponse:
    """Sync a run to Google Calendar (placeholder implementation).

    Args:
        run_id: The ID of the run to sync.

    Returns:
        SyncResponse indicating the result of the sync operation.

    Note:
        This is a placeholder implementation that creates a mock sync record.
        Real Google Calendar integration will be added later.
    """
    # Check if run is already synced
    existing_sync = get_synced_run(run_id)
    if existing_sync and existing_sync.sync_status == "synced":
        return SyncResponse(
            success=False,
            message=f"Run {run_id} is already synced to Google Calendar",
            google_event_id=existing_sync.google_event_id,
            sync_status=existing_sync.sync_status,
            synced_at=existing_sync.synced_at,
        )

    # TODO: Replace with actual Google Calendar API integration
    # For now, create a mock sync record
    try:
        mock_google_event_id = f"mock_event_{run_id}_{hash(run_id) % 10000}"

        if existing_sync:
            # Update existing failed sync
            updated_sync = update_synced_run(
                run_id=run_id,
                google_event_id=mock_google_event_id,
                sync_status="synced",
                clear_error_message=True,
            )
            if updated_sync is None:
                raise HTTPException(
                    status_code=500, detail="Failed to update sync record"
                )
            synced_run = updated_sync
        else:
            # Create new sync record
            synced_run = create_synced_run(
                run_id=run_id,
                google_event_id=mock_google_event_id,
                run_version=1,
                sync_status="synced",
            )

        return SyncResponse(
            success=True,
            message=f"Successfully synced run {run_id} to Google Calendar",
            google_event_id=synced_run.google_event_id,
            sync_status=synced_run.sync_status,
            synced_at=synced_run.synced_at,
        )

    except Exception as e:
        # Handle database errors
        error_msg = f"Failed to sync run {run_id}: {str(e)}"

        # Try to create/update a failed sync record
        try:
            if existing_sync:
                update_synced_run(
                    run_id=run_id,
                    sync_status="failed",
                    error_message=error_msg,
                )
            else:
                create_synced_run(
                    run_id=run_id,
                    google_event_id="",
                    sync_status="failed",
                    error_message=error_msg,
                )
        except Exception:
            # If we can't even create a failed record, just log it
            pass

        return SyncResponse(
            success=False,
            message=error_msg,
            google_event_id=None,
            sync_status="failed",
            synced_at=None,
        )


@router.delete("/runs/{run_id}", response_model=SyncResponse)
def unsync_run_from_calendar(run_id: str) -> SyncResponse:
    """Remove a run's sync from Google Calendar (placeholder implementation).

    Args:
        run_id: The ID of the run to unsync.

    Returns:
        SyncResponse indicating the result of the unsync operation.

    Note:
        This is a placeholder implementation that removes the sync record.
        Real Google Calendar integration will be added later.
    """
    synced_run = get_synced_run(run_id)

    if synced_run is None:
        return SyncResponse(
            success=False,
            message=f"Run {run_id} is not currently synced",
            google_event_id=None,
            sync_status="failed",
            synced_at=None,
        )

    # TODO: Replace with actual Google Calendar API to delete the event
    # For now, just delete the database record

    deleted = delete_synced_run(run_id)

    if deleted:
        return SyncResponse(
            success=True,
            message=f"Successfully removed sync for run {run_id}",
            google_event_id=synced_run.google_event_id,
            sync_status="failed",  # No longer synced
            synced_at=None,
        )
    else:
        return SyncResponse(
            success=False,
            message=f"Failed to remove sync for run {run_id}",
            google_event_id=synced_run.google_event_id,
            sync_status=synced_run.sync_status,
            synced_at=synced_run.synced_at,
        )


@router.get("/runs", response_model=List[SyncedRun])
def get_all_sync_records() -> List[SyncedRun]:
    """Get all sync records for debugging/admin purposes.

    Returns:
        List of all SyncedRun records.
    """
    return get_all_synced_runs()


@router.get("/runs/failed", response_model=List[SyncedRun])
def get_failed_sync_records() -> List[SyncedRun]:
    """Get all runs with failed sync status for retry/debugging.

    Returns:
        List of SyncedRun records with 'failed' status.
    """
    return get_failed_syncs()
