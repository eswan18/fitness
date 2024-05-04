import sys
import streamlit as st
import pandas as pd

from fitness.cleaning import clean
from fitness.summaries import totals
from fitness.filters import filter_by_dates
from fitness.charts import mileage_density, mileage_histogram, shoe_usage
from fitness.load import load_and_clean

# Load and clean data.
filename = sys.argv[1]
df = load_and_clean(filename)

st.title("Running")

# Filters.
col1, col2, col3 = st.columns(3)
date_min, date_max = df["Date"].min(), df["Date"].max()
start_date = col1.date_input(
    "Start date", value=date_min, min_value=date_min, max_value=date_max
)
end_date = col2.date_input(
    "End date", value=date_max, min_value=date_min, max_value=date_max
)
n_days = (end_date - start_date).days + 1
df = filter_by_dates(df, start=start_date, end=end_date)


total_metrics = totals(df)


st.divider()
main_metrics_container = st.container()
col1, col2, col3, col4 = main_metrics_container.columns(4)
col1.subheader(f"**{total_metrics.count}**", anchor=False)
col1.caption(f"Total runs")
col2.subheader(f"**{total_metrics.miles:0.0f}**", anchor=False)
col2.caption(f"Total miles")
col3.subheader(f"**{total_metrics.miles / total_metrics.runs:0.2f}**", anchor=False)
col3.caption(f"Average miles per run")
col4.subheader(f"**{total_metrics.miles / n_days:0.2f}**", anchor=False)
col4.caption(f"Average miles per day")

st.divider()
other_metrics_container = st.container()
_, col2_1, col2_2, _ = other_metrics_container.columns(4)
col2_1.subheader(f"**{total_metrics.minutes:0,.0f}**", anchor=False)
col2_1.caption(f"Total minutes")
col2_2.subheader(f"**{total_metrics.calories:0,.0f}**", anchor=False)
col2_2.caption(f"Total calories")

mileage_tab, shoe_tab = st.tabs(["Mileage Density", "Shoe Usage"])
mileage_tab_container = mileage_tab.container()
col1, col2 = mileage_tab_container.columns(2)
bw_adjust = mileage_tab_container.slider("KDE Smoothing", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
col1.pyplot(mileage_density(df, bw_adjust=bw_adjust))
col2.pyplot(mileage_histogram(df))
shoe_tab.altair_chart(shoe_usage(df), use_container_width=True)
