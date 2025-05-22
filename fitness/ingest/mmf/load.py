from pathlib import Path
import os
import csv
from .models import MmfActivity


def load_mmf_data(mmf_file: Path | None = None) -> list[MmfActivity]:
    if mmf_file is None:
        mmf_file = Path(os.environ["MMF_DATAFILE"])
    with open(mmf_file, "r") as f:
        reader = csv.DictReader(f)
        records = [MmfActivity.model_validate(row) for row in reader]
    return records


def load_mmf_runs(mmf_file: Path | None = None) -> list[MmfActivity]:
    """Load the MMF data from a file."""
    records = load_mmf_data(mmf_file)
    # Filter the records to only include runs.
    records = [
        record
        for record in records
        if record.activity_type in ["Run", "Indoor Run / Jog"]
    ]
    return records
