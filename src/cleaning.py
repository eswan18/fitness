import pandas as pd


def filter_to_runs(df: pd.DataFrame) -> pd.DataFrame:
    """Only keep indoor and outdoor runs."""
    activity_types = ["Run", "Indoor Run / Jog"]
    return df[df["Activity Type"].isin(activity_types)].copy()

def timestamp_from_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the "Workout Date" column into a datetime."""
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Workout Date'])
    # Also add some columns for Day, Month, Year
    df['Day of Month'] = df['Date'].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df = df.drop(columns=['Workout Date'])
    return df

def create_shoes_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create a column for shoes."""
    df = df.copy()
    shoes = df['Notes'].str.extract(r"b'.*Shoes: ([^\\]*).*'", expand=False).str.strip()
    # There are some inconsistencies in the shoe names that we can fix.
    transforms = {
        'M1080K10': 'New Balance M1080K10',
        'New Balance 1080K10': 'New Balance M1080K10',
        'M1080R10': 'New Balance M1080R10',
    }
    df['Shoes'] = shoes.replace(transforms)
    return df


cleaning_functions = [
    filter_to_runs,
    timestamp_from_date_column,
    create_shoes_column,
]