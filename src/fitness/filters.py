from datetime import date
import pandas as pd

def filter_by_dates(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Filter the dataframe to only include dates between start and end."""
    return df[(df['Date'].dt.date >= start) & (df['Date'].dt.date <= end)].copy()