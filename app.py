import streamlit as st
import pandas as pd
from sodapy import Socrata
from dataclasses import dataclass
@dataclass
class DatasetURL:
    domain = "data.cityofnewyork.us"
    dataset = "h9gi-nx95"

@st.cache_data
def load_data(url_object: DatasetURL, nrow: int) -> pd.DataFrame:
    """

    :param url_object: @dataclass object with two values: domain and dataset
    :param nrow: an integer that specifies the number of rows to fetch
    :return: pd.DataFrame
    """
    client = Socrata(url_object.domain, None)
    results = client.get(url_object.dataset, limit=nrow)

    results_df = pd.DataFrame.from_records(results)
    # parse the dates as pandas date objects
    results_df['crash_date'] = pd.to_datetime(results_df['crash_date'])
    results_df['crash_time'] = pd.to_datetime(results_df['crash_time'])

    results_df.dropna(subset=['latitude', 'longitude'], inplace=True)

    return results_df

data = None
#%%
st.sidebar.header("Adjust dataset size")
with st.sidebar:
    user_nrow = 2_000
    with st.form(key="submit"):
        user_nrow = st.number_input("Enter dataset size", min_value=2_000, max_value=2_000_000)
        submit_button = st.form_submit_button("Set")

    data = load_data(DatasetURL(), user_nrow)

    with st.popover("Show Raw Data"):
        st.subheader("Raw Data")
        st.write(data)


if submit_button:
    st.toast(f"Size set to: {user_nrow}")

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in New York City.")


