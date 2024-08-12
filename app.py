import numpy as np
import streamlit as st
import pandas as pd
from sodapy import Socrata
import plotly.express as px
import pydeck as pdk
from dataclasses import dataclass
from datetime import datetime as dt
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

    # Convert 'number_of_persons_injured' to numeric, handling errors
    results_df['number_of_persons_injured'] = pd.to_numeric(results_df['number_of_persons_injured'], errors='coerce')
    results_df['number_of_persons_injured'].fillna(0, inplace=True)

    # Convert 'number_of_pedestrians_injured' to numeric, handling errors
    results_df['number_of_pedestrians_injured'] = pd.to_numeric(results_df['number_of_pedestrians_injured'], errors='coerce')
    results_df['number_of_pedestrians_injured'].fillna(0, inplace=True)

    # Convert 'number_of_cyclist_injured' to numeric, handling errors
    results_df['number_of_cyclist_injured'] = pd.to_numeric(results_df['number_of_cyclist_injured'], errors='coerce')
    results_df['number_of_cyclist_injured'].fillna(0, inplace=True)

    # Convert 'number_of_pedestrians_injured' to numeric, handling errors
    results_df['number_of_motorist_injured'] = pd.to_numeric(results_df['number_of_motorist_injured'], errors='coerce')
    results_df['number_of_motorist_injured'].fillna(0, inplace=True)

    # Ensure latitude and longitude are floats
    results_df['latitude'] = pd.to_numeric(results_df['latitude'], errors='coerce')
    results_df['longitude'] = pd.to_numeric(results_df['longitude'], errors='coerce')

    # Drop rows with missing latitude and longitude
    results_df.dropna(subset=['latitude', 'longitude'], inplace=True)

    return results_df


st.set_page_config(page_title="Vehicle Collisions in NYC", layout="wide")

st.sidebar.header("Adjust dataset size")
with st.sidebar.form(key="submit"):
    user_nrow = st.number_input("Enter dataset size", min_value=2_000, max_value=2_000_000)
    submit_button = st.form_submit_button("Set")

data = load_data(DatasetURL(), user_nrow)
original_data = data

with st.sidebar.popover("Show Raw Data"):
    st.subheader("Raw Data")
    st.write(data)


if submit_button:
    st.toast(f"Size set to: {user_nrow}")

st.title("Motor Vehicle Collisions in New York City")
st.write("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in New York City.")

st.header("Where have most people been injured in NYC?")
injured_people = st.slider("Number of injured persons", 0, 19)
st.map(data.query("number_of_persons_injured >= @injured_people")[['latitude', 'longitude']].dropna(how="any"))

st.header("How many collisions have occurred during a given time of day?")
hour = st.selectbox("Select Hour", range(0, 24), 19)
data = data[data['crash_time'].dt.hour == hour]


with st.popover(f"Show subset data [{dt.now().replace(hour=hour, minute=0).strftime("%H:%M")} and {dt.now().replace(hour=hour+1, minute=0).strftime("%H:%M")}]"):
    st.subheader(f"Raw data for {dt.now().replace(hour=hour, minute=0).strftime("%H:%M")} and {dt.now().replace(hour=hour+1, minute=0).strftime("%H:%M")}")
    st.write(data)

midpoint = (np.average(data['latitude']), np.average(data['longitude']))

hour_tab, minute_tab = st.tabs(["By Hour", "By Minute"])

with hour_tab:
    st.markdown("### By Hour")
    st.markdown(f"Breakdown by hour between {dt.now().replace(hour=hour, minute=0).strftime("%H:%M")} and {dt.now().replace(hour=hour + 1, minute=0).strftime("%H:%M")}")
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 11,
            "pitch": 70,
        },
        layers=[
            pdk.Layer("HexagonLayer", data=data[["crash_time", "latitude", "longitude"]], get_position=["longitude", "latitude"], radius=100, extruded=True, pickable=True, elevation_scale=4, elevation_range=[0, 1000])
        ]
    ))

with minute_tab:
    st.markdown("### By Minute")
    st.markdown(f"Breakdown by minute between {dt.now().replace(hour=hour, minute=0).strftime("%H:%M")} and {dt.now().replace(hour=hour+1, minute=0).strftime("%H:%M")}")
    filtered = data[
        (data["crash_time"].dt.hour >= hour) & (data["crash_time"].dt.hour <= (hour + 1))
    ]

    hist = np.histogram(filtered["crash_time"].dt.minute, bins=60, range=(0, 60))[0]
    chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
    fig = px.bar(chart_data, x="minute", y="crashes", hover_data=["minute", "crashes"], height=400)
    st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ["Pedestrians", "Cyclists", "Motorists"])

if select == "Pedestrians":
    st.write(original_data.query("number_of_pedestrians_injured >= 1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=["number_of_pedestrians_injured"], ascending=False).dropna(how="any")[:5])
elif select == "Cyclists":
    st.write(original_data.query("number_of_cyclist_injured >= 1")[["on_street_name", "number_of_cyclist_injured"]].sort_values(by=["number_of_cyclist_injured"], ascending=False).dropna(how="any")[:5])
else:
    st.write(original_data.query("number_of_motorist_injured >= 1")[["on_street_name", "number_of_motorist_injured"]].sort_values(by=["number_of_motorist_injured"], ascending=False).dropna(how="any")[:5])
