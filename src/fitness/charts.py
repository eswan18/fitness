import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt


def mileage_density(df: pd.DataFrame):
    """Create a density chart over time, weightd by miles."""
    fig, ax = plt.subplots(figsize=(12, 6))
    # Weight each run by the number of miles.
    sns.kdeplot(df, x="Date", weights=df["Distance (mi)"], bw_adjust=0.3, ax=ax)
    return fig


def shoe_usage(df: pd.DataFrame) -> alt.Chart:
    """Create a chart of miles by shoe."""
    miles_by_shoe = df.groupby("Shoes", as_index=False)["Distance (mi)"].sum()
    chart = (
        alt.Chart(miles_by_shoe)
        .mark_bar()
        .encode(
            x="Distance (mi):Q",
            y="Shoes:N",
        )
    )
    return chart
