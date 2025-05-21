from typing import Annotated
import os
from pathlib import Path
import csv

from pydantic import BaseModel, Field, BeforeValidator

# Validation validation_aliases
# Date Submitted,Workout Date,Activity Type,Calories Burned (kCal),Distance (mi),Workout Time (seconds),Avg Pace (min/mi),Max Pace (min/mi),Avg Speed (mi/h),Max Speed (mi/h),Avg Heart Rate,Steps,Notes,Source,Link


def empty_str_to_none(v):
    if v == "":
        return None
    return v


class MmfRun(BaseModel):
    date_submitted: str = Field(validation_alias="Date Submitted")
    workout_date: str = Field(validation_alias="Workout Date")
    activity_type: str = Field(validation_alias="Activity Type")
    calories_burned: float = Field(validation_alias="Calories Burned (kCal)")
    distance: float = Field(validation_alias="Distance (mi)")
    workout_time: float = Field(validation_alias="Workout Time (seconds)")
    avg_pace: float = Field(validation_alias="Avg Pace (min/mi)")
    max_pace: float = Field(validation_alias="Max Pace (min/mi)")
    avg_speed: float = Field(validation_alias="Avg Speed (mi/h)")
    max_speed: float = Field(validation_alias="Max Speed (mi/h)")
    avg_heart_rate: Annotated[float | None, BeforeValidator(empty_str_to_none)] = Field(
        validation_alias="Avg Heart Rate",
    )
    steps: Annotated[int | None, BeforeValidator(empty_str_to_none)] = Field(
        validation_alias="Steps"
    )
    notes: str = Field(validation_alias="Notes")
    source: str = Field(validation_alias="Source")
    link: str = Field(validation_alias="Link")


def load_mmf_data(mmf_file: Path | None = None) -> list[MmfRun]:
    if mmf_file is None:
        mmf_file = Path(os.environ["MMF_DATAFILE"])
    with open(mmf_file, "r") as f:
        reader = csv.DictReader(f)
        runs = [MmfRun.model_validate(row) for row in reader]
    return runs
