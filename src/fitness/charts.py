import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt


def mileage_density(df: pd.DataFrame, bw_adjust: float = 0.3):
    """Create a density chart over time, weightd by miles."""
    fig, ax = plt.subplots(figsize=(12, 6))
    # Weight each run by the number of miles.
    sns.kdeplot(df, x="Date", weights=df["Distance (mi)"], bw_adjust=bw_adjust, ax=ax)
    return fig


def mileage_histogram(df: pd.DataFrame):
    # Calculate the number of bins - should be roughly 30.
    n_days = (df["Date"].max() - df["Date"].min()).days + 1
    if n_days <= 30:
        bins = n_days
    elif n_days <= 60:
        bins = n_days // 2
    else:
        bins = 30
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(df, x="Date", weights=df["Distance (mi)"], bins=bins, ax=ax)
    return fig


def shoe_usage(df: pd.DataFrame, order_by_mileage: bool = False) -> alt.Chart:
    """Create a chart of miles by shoe."""
    miles_by_shoe = df.groupby("Shoes", as_index=False)["Distance (mi)"].sum()
    y = alt.Y("Shoes:N")
    if order_by_mileage:
        y = y.sort("-x")
    chart = (
        alt.Chart(miles_by_shoe)
        .mark_bar()
        .encode(x="Distance (mi):Q", y=y)
    )
    return chart
