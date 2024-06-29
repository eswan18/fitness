import pandas as pd

KEEP_COLS = [
    "Activity Type",
    "Activity Date",
    "Elapsed Time",
    "Distance",
    "Activity Private Note",
    "Activity Gear",
    "Calories",
]


def _filter_to_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Only keep indoor and outdoor runs."""
    return df[df["Activity Type"] == "Run"].copy()


def _convert_km_to_miles(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Distance from km to miles."""
    df = df.copy()
    df["Distance"] = df["Distance"] * 0.621371
    return df


def _remote_unneeded_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limit down to just the columns we need."""
    return df[KEEP_COLS].copy()


def _parse_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the date column."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Activity Date"], format="%b %d, %Y, %I:%M:%S %p")
    df = df.drop(columns=["Activity Date"])
    # The data comes in UTC, so we need to localize it.
    df["Date"] = df["Date"].dt.tz_localize("UTC")
    df["Date"] = df["Date"].dt.tz_convert("America/Chicago")
    # In order to compare to other timezone-naive data, we need to remove the timezone.
    df["Date"] = df["Date"].dt.tz_localize(None)
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename some columns to match the MMF columns."""
    df = df.copy()
    mapping = {
        "Elapsed Time": "Workout Time (seconds)",
        "Distance": "Distance (mi)",
        "Activity Gear": "Shoes",
        "Activity Private Note": "Notes",
        "Calories": "Calories Burned (kCal)",
    }
    for old_name, new_name in mapping.items():
        df[new_name] = df[old_name]
        df.drop(columns=[old_name], inplace=True)
    return df


def _add_source_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column for the source of the data."""
    df = df.copy()
    df["Source"] = "Strava"
    return df


def _rename_shoes(df: pd.DataFrame) -> pd.DataFrame:
    transforms = {
        "Adizero SL": "Adidas Adizero SL",
        "Ghost 15": "Brooks Ghost 15",
        "Pegasus 38": "Nike Air Zoom Pegasus 38",
    }
    df = df.copy()
    df["Shoes"] = df["Shoes"].replace(transforms)
    return df


_cleaning_functions = [
    _filter_to_runs,
    _convert_km_to_miles,
    _remote_unneeded_columns,
    _parse_date,
    _rename_columns,
    _add_source_column,
    _rename_shoes,
]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe."""
    for cleaning_function in _cleaning_functions:
        df = cleaning_function(df)
    return df
