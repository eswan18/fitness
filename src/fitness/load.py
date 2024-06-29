import streamlit as st
import pandas as pd

from . import mmf, strava


@st.cache_data
def load_and_clean(mmf_filename: str, strava_filename: str) -> pd.DataFrame:
    """Load data from MapMyFitness and Strava and clean it."""
    mmf_df = load_and_clean_mmf(mmf_filename)
    strava_df = load_and_clean_strava(strava_filename)
    # Combine the two dataframes.
    return pd.concat([mmf_df, strava_df], ignore_index=True)


@st.cache_data
def load_and_clean_mmf(filename: str) -> pd.DataFrame:
    """Load MapMyFitness data and clean it."""
    df = pd.read_csv(filename)
    df = mmf.clean(df)
    return df


@st.cache_data
def load_and_clean_strava(filename: str) -> pd.DataFrame:
    """Load Strava data and clean it."""
    df = pd.read_csv(filename)
    df = strava.clean(df)
    return df
