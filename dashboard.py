import sys
import streamlit as st
import pandas as pd

from fitness.cleaning import clean
from fitness.summaries import totals
from fitness.filters import filter_by_dates
from fitness.charts import mileage_density, shoe_usage

# Load and clean data.
filename = sys.argv[1]
df = pd.read_csv(filename)
df = clean(df)

# Filters.
col1, col2 = st.columns(2)
date_min, date_max = df['Date'].min(), df['Date'].max()
start_date = col1.date_input("Start date", value=date_min, min_value=date_min, max_value=date_max)
end_date = col2.date_input("End date", value=date_max, min_value=date_min, max_value=date_max)
df = filter_by_dates(df, start=start_date, end=end_date)


totals_container = st.container()
col1, col2, col3, col4 = totals_container.columns(4)
total_metrics = totals(df)
col1.markdown(f"Total runs: **{total_metrics.count}**")
col2.markdown(f"Total miles: **{total_metrics.miles:0.0f}**")
col3.markdown(f"Total minutes: **{total_metrics.minutes:0,.0f}**")
col4.markdown(f"Total calories: **{total_metrics.calories:,}**")

tabs = st.tabs(["Mileage Density", "Shoe Usage"])
tabs[0].pyplot(mileage_density(df))
tabs[1].altair_chart(shoe_usage(df), use_container_width=True)