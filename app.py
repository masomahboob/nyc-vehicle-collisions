import streamlit as st
import pandas as pd
from sodapy import Socrata

client = Socrata("data.cityofnewyork.us", None)
results = client.get("h9gi-nx95", limit=500_000)

results_df = pd.DataFrame.from_records(results)

print(results_df.head())
