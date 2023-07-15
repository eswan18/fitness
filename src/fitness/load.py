import pandas as pd
from .cleaning import clean
import streamlit as st

@st.cache_data
def load_and_clean(filename: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    df = pd.read_csv(filename)
    df = clean(df)
    return df