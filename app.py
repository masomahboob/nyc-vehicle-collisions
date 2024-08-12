import streamlit as st
import pandas as pd
from sodapy import Socrata
from dataclasses import dataclass
@dataclass
class DatasetURL:
    domain = "data.cityofnewyork.us"
    dataset = "h9gi-nx95"

@st.cache_data
def load_data(url_object: DatasetURL, nrow: int = 2_000) -> pd.DataFrame:
    client = Socrata(url_object.domain, None)
    results = client.get(url_object.dataset, limit=nrow)

    results_df = pd.DataFrame.from_records(results)
    # parse the dates as pandas date objects
    results_df['crash_date'] = pd.to_datetime(results_df['crash_date'])
    results_df['crash_time'] = pd.to_datetime(results_df['crash_time'])

    results_df.dropna(subset=['latitude', 'longitude'], inplace=True)

    return results_df
#%%

data = load_data(DatasetURL(), 100_000)
print(data.head())

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in New York City.")

