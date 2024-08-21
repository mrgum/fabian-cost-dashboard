import streamlit as st
from datetime import date, timedelta

start_time = st.slider(
    "When do you start?",
    value=date(2024, 1, 1),
    format="YYYY-MM",
    min_value=date(2024, 1, 1),
    max_value=date(2024, 8, 1),
    step=timedelta(days=1)
)
st.write("Start time:", start_time)
