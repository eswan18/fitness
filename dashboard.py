import sys
import streamlit as st
import pandas as pd

from fitness.cleaning import clean
from fitness.summaries import totals
from fitness.filters import filter_by_dates
from fitness.charts import mileage_density, shoe_usage
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
df = filter_by_dates(df, start=start_date, end=end_date)
st.divider()


totals_container = st.container()
col1, col2, col3, col4 = totals_container.columns(4)
total_metrics = totals(df)

col1.subheader(f"**{total_metrics.count}**", anchor=False)
col1.caption(f"Total runs")
col2.subheader(f"**{total_metrics.miles:0.0f}**", anchor=False)
col2.caption(f"Total miles")
col3.subheader(f"**{total_metrics.minutes:0,.0f}**", anchor=False)
col3.caption(f"Total minutes")
col4.subheader(f"**{total_metrics.calories:0,.0f}**", anchor=False)
col4.caption(f"Total calories")

tabs = st.tabs(["Mileage Density", "Shoe Usage"])
tabs[0].pyplot(mileage_density(df))
tabs[1].altair_chart(shoe_usage(df), use_container_width=True)
