import logging
from pathlib import Path
import os
import csv
import zoneinfo

from datetime import datetime, timezone, date

from .models import MmfActivity

logger = logging.getLogger(__name__)


def load_mmf_data(
    mmf_file: Path | None = None, mmf_timezone: str | None = None
) -> list[MmfActivity]:
    """Load raw MMF activities from a CSV and normalize dates.

    Args:
        mmf_file: Optional path to the CSV file. If None, reads MMF_DATAFILE env var.
        mmf_timezone: Optional IANA timezone name for interpreting local dates.
            Defaults to MMF_TIMEZONE env var or "America/Chicago".

    Returns:
        List of activities with `workout_date_utc` populated.
    """
    logger.info("Starting MMF data load")

    if mmf_file is None:
        try:
            mmf_file_path = os.environ["MMF_DATAFILE"]
        except KeyError:
            raise ValueError(
                "MMF_DATAFILE environment variable is required but not set"
            )
        if mmf_file_path == "__skip__":
            logger.info("MMF data loading skipped")
            return []

        mmf_file = Path(mmf_file_path)
        if not mmf_file.exists():
            logger.error(f"MMF data file does not exist: {mmf_file}")
            raise FileNotFoundError(f"MMF data file does not exist: {mmf_file}")

    if mmf_timezone is None:
        mmf_timezone = os.environ.get("MMF_TIMEZONE", "America/Chicago")
        logger.debug(f"Using timezone: {mmf_timezone}")

    logger.info(f"Loading MMF data from file: {mmf_file}")
    logger.info(f"Using timezone for date conversion: {mmf_timezone}")

    tz = zoneinfo.ZoneInfo(mmf_timezone)

    try:
        with open(mmf_file, "r") as f:
            reader = csv.DictReader(f)
            records = []
            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 (header is row 1)
                try:
                    activity = MmfActivity.model_validate(row)
                    # Convert the workout_date from local timezone to UTC
                    activity.workout_date_utc = _convert_date_to_utc(
                        activity.workout_date, tz
                    )
                    records.append(activity)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse MMF activity at row {row_num}: {type(e).__name__}: {str(e)}"
                    )
                    logger.debug(f"Problematic row data: {row}")
                    # Continue processing other rows

        logger.info(f"Successfully loaded {len(records)} activities from MMF CSV file")
        return records

    except Exception as e:
        logger.error(
            f"Failed to load MMF data from {mmf_file}: {type(e).__name__}: {str(e)}",
            exc_info=True,
        )
        raise


def _convert_date_to_utc(local_date: date, local_tz: zoneinfo.ZoneInfo) -> date:
    """Convert a naive date to UTC by assuming it represents the start of day in local_tz."""
    # Assume the date represents the start of the day in the local timezone
    local_datetime = datetime.combine(local_date, datetime.min.time())
    # Make it timezone-aware
    local_aware = local_datetime.replace(tzinfo=local_tz)
    # Convert to UTC
    utc_datetime = local_aware.astimezone(timezone.utc)
    # Return just the date portion
    return utc_datetime.date()


def load_mmf_runs(
    mmf_file: Path | None = None, mmf_timezone: str | None = None
) -> list[MmfActivity]:
    """Load the MMF data from a file.

    Returns only activities classified as runs.
    """
    logger.info("Loading MMF runs (filtering to run activities only)")
    records = load_mmf_data(mmf_file, mmf_timezone)

    # Filter the records to only include runs.
    initial_count = len(records)
    records = [
        record
        for record in records
        if record.activity_type in ["Run", "Indoor Run / Jog"]
    ]
    filtered_count = initial_count - len(records)

    logger.info(
        f"Filtered MMF activities to {len(records)} runs "
        f"(excluded {filtered_count} non-run activities)"
    )

    return records
