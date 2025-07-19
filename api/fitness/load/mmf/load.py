from pathlib import Path
import os
import csv
import zoneinfo
from datetime import datetime, timezone, date
from .models import MmfActivity


def load_mmf_data(mmf_file: Path | None = None, mmf_timezone: str | None = None) -> list[MmfActivity]:
    if mmf_file is None:
        try:
            mmf_file = Path(os.environ["MMF_DATAFILE"])
        except KeyError:
            raise ValueError(
                "MMF_DATAFILE environment variable is required but not set"
            ) from None
    
    if mmf_timezone is None:
        mmf_timezone = os.environ.get("MMF_TIMEZONE", "America/Chicago")
    
    tz = zoneinfo.ZoneInfo(mmf_timezone)
    
    with open(mmf_file, "r") as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            activity = MmfActivity.model_validate(row)
            # Convert the workout_date from local timezone to UTC
            activity.workout_date_utc = _convert_date_to_utc(activity.workout_date, tz)
            records.append(activity)
    return records


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


def load_mmf_runs(mmf_file: Path | None = None, mmf_timezone: str | None = None) -> list[MmfActivity]:
    """Load the MMF data from a file."""
    records = load_mmf_data(mmf_file, mmf_timezone)
    # Filter the records to only include runs.
    records = [
        record
        for record in records
        if record.activity_type in ["Run", "Indoor Run / Jog"]
    ]
    return records
