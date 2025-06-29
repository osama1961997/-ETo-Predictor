import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import folium
from streamlit_folium import st_folium

# === 1. Load resources ===


@st.cache_data
def load_governorate_data():
    return pd.read_excel("governerate lat_ lon.xlsx")


@st.cache_resource
def load_model():
    return joblib.load("LAT_LONG_Tmax _model.pkl")


# === 2. App interface ===
st.title("📍 ETo Prediction for a Specific Location")
st.write("Select a date, choose a governorate or enter coordinates manually, and provide Tmax to predict ETo.")

# === 3. Date input ===
selected_date = st.date_input("Select a date", value=datetime(2025, 2, 1))
year = selected_date.year
J = selected_date.timetuple().tm_yday
date_str = selected_date.strftime("%Y-%m-%d")
st.write(f"🗓️ **Day of Year (J)**: `{J}`")

# === 4. Governorate selection or manual input ===
gov_data = load_governorate_data()
gov_names = list(gov_data["governorate"].dropna().unique())

gov_choice = st.selectbox("Select Governorate", options=[
                          "-- Manual Entry --"] + gov_names)

if gov_choice != "-- Manual Entry --":
    selected_row = gov_data[gov_data["governorate"] == gov_choice].iloc[0]
    latitude = selected_row["Latitude"]
    longitude = selected_row["Longitude"]
    st.success(
        f"📌 Coordinates from governorate: **Lat = {latitude}, Lon = {longitude}**")
else:
    latitude = st.number_input("Enter Latitude", format="%.6f")
    longitude = st.number_input("Enter Longitude", format="%.6f")

# === 5. Input Tmax ===
tmax = st.number_input("🌡️ Enter Maximum Temperature (°C)", format="%.2f")

# === 6. Predict button ===
if st.button("🔍 Predict and Show Location on Map"):
    if latitude and longitude and tmax:
        model = load_model()
        input_df = pd.DataFrame({
            'latitude': [latitude],
            'Longitude': [longitude],
            'J': [J],
            'Tmax': [tmax]
        })

        eto = model.predict(input_df)[0]
        st.success(f"✅ Predicted ETo for {date_str} is: **{eto:.2f} mm/day**")

        # === 7. Show on Folium Map ===
        st.subheader("🗺️ Location on Map")
        m = folium.Map(location=[latitude, longitude], zoom_start=6)
        folium.Marker(
            [latitude, longitude],
            popup=f"ETo: {eto:.2f} mm/day",
            tooltip="Selected Location",
            icon=folium.Icon(color="green", icon="cloud")
        ).add_to(m)

        st_folium(m, width=700, height=500)
    else:
        st.warning("Please make sure all inputs are filled.")
