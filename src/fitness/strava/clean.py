import pandas as pd


_KEEP_COLS = [
    "type",
    "start_date_local",
    "elapsed_time",
    "distance",
    "shoes",
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe."""
    for cleaning_function in _cleaning_functions:
        df = cleaning_function(df)
    return df


def _filter_to_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Only keep indoor and outdoor runs."""
    return df[df["type"] == "Run"].copy()


def _convert_km_to_miles(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Distance from meters to miles."""
    df = df.copy()
    df["Distance (mi)"] = df["distance"] / 1609.34
    df = df.drop(columns=["distance"])
    return df


def _remove_unneeded_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limit down to just the columns we need."""
    return df[_KEEP_COLS].copy()


def _parse_date(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the date column."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["start_date_local"])
    df = df.drop(columns=["start_date_local"])
    df["Date"] = df["Date"].dt.tz_localize(None)
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename some columns to match the MMF columns."""
    df = df.copy()
    mapping = {
        "elapsed_time": "Workout Time (seconds)",
        "shoes": "Shoes",
        # "Calories": "Calories Burned (kCal)",
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
    _remove_unneeded_columns,
    _convert_km_to_miles,
    _parse_date,
    _rename_columns,
    _add_source_column,
    _rename_shoes,
]
