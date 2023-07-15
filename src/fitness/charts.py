import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

def mileage_density(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 6))
    # Weight each run by the number of miles.
    sns.kdeplot(df, x='Date', weights=df['Distance (mi)'], bw=0.08, ax=ax)
    return fig

def shoe_usage(df: pd.DataFrame) -> alt.Chart:
    miles_by_shoe = df.groupby('Shoes', as_index=False)['Distance (mi)'].sum()
    chart = alt.Chart(miles_by_shoe).mark_bar().encode(
        x='Distance (mi):Q',
        y='Shoes:N',
    )
    return chart