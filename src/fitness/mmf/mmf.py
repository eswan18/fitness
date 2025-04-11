"""Utility functions for working specifically with data downloaded from MapMyFitness."""

import pandas as pd


def _filter_to_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Only keep indoor and outdoor runs."""
    activity_types = ["Run", "Indoor Run / Jog"]
    return df[df["Activity Type"].isin(activity_types)].copy()


def _timestamp_from_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the "Workout Date" column into a datetime."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Workout Date"], format="mixed")
    # Also add some columns for Day, Month, Year
    df["Day of Month"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df = df.drop(columns=["Workout Date"])
    return df


def _create_shoes_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create a column for shoes."""
    df = df.copy()
    shoes = df["Notes"].str.extract(r".*Shoes: ([^\n]*)", expand=False).str.strip()
    # There are some inconsistencies in the shoe names that we can fix.
    transforms = {
        "M1080K10": "New Balance M1080K10",
        "New Balance 1080K10": "New Balance M1080K10",
        "M1080R10": "New Balance M1080R10",
    }
    df["Shoes"] = shoes.replace(transforms)
    return df


def _add_source_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column for the source of the data."""
    df = df.copy()
    df["Source"] = "MapMyFitness"
    return df


_cleaning_functions = [
    _filter_to_runs,
    _timestamp_from_date_column,
    _create_shoes_column,
    _add_source_column,
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe."""
    for cleaning_function in _cleaning_functions:
        df = cleaning_function(df)
    return df
