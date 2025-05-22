from typing import Annotated, Literal
from datetime import date, datetime
import re

from pydantic import BaseModel, Field, BeforeValidator

# There are some cases where the shoe names are inconsistent in the data.
# This remaps them to a consistent name.
SHOE_RENAME_MAP = {
    "M1080K10": "New Balance M1080K10",
    "M1080R10": "New Balance M1080R10",
    "New Balance 1080K10": "New Balance M1080K10",
    "Karhu Fusion 2021  2": "Karhu Fusion 2021 - 2",
    "Karhu Fusion 2021 2": "Karhu Fusion 2021 - 2",
}

MmfActivityType = Literal[
    "Bike Ride",
    "Gym Workout",
    "Indoor Run / Jog",
    "Machine Workout",
    "Run",
    "Walk",
    "Weight Workout",
]


def empty_str_to_none(v):
    """
    Convert an empty string to None, or leave the value as is.

    A few numeric fields comes in as empty strings when they're not set. Pydantic throws
    type errors if we don't convert them.
    """
    if v == "":
        return None
    return v


def parse_date(v) -> date:
    """
    Convert a date string in the format 'May 6, 2025' to '2025-05-06'.

    Dates come in as 'May 6, 2025' or 'Jan. 14, 2025' or 'Sept. 24, 2024' but Pydantic
    expects 'YYYY-MM-DD'.
    """
    # 1) Strip any dots on month abbreviations
    clean = v.replace(".", "")  # remove any trailing dots on abbreviations
    # 2) Normalize "Sept" → "Sep" (so it matches %b)
    clean = re.sub(r"\bSept\b", "Sep", clean, flags=re.IGNORECASE)
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date string not in expected format: {v!r}")


class MmfActivity(BaseModel):
    date_submitted: Annotated[date, BeforeValidator(parse_date)] = Field(
        validation_alias="Date Submitted"
    )
    workout_date: Annotated[date, BeforeValidator(parse_date)] = Field(
        validation_alias="Workout Date"
    )
    activity_type: MmfActivityType = Field(validation_alias="Activity Type")
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

    def shoes(self) -> str | None:
        """
        Extract the shoes from the notes field.

        Shoes are in the format 'Shoes: <shoe name>'.
        """
        match = re.search(r"Shoes:\s*(.+)", self.notes)
        if match:
            raw_shoe_name = match.group(1).strip()
            if raw_shoe_name in SHOE_RENAME_MAP:
                # If the shoe name is in the rename mapping, use the mapped name
                return SHOE_RENAME_MAP[raw_shoe_name]
            else:
                return raw_shoe_name
        return None
