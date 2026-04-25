import streamlit as st
import pandas as pd
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- HIGH-VISIBILITY CSS (Wahi professional look) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800 !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
    .status-box { padding: 15px; background-color: #1c2128; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; font-weight: bold; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #8b949e; border-top: 1px solid #30363d; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ACCURATE WEATHER FUNCTION ---
def get_realtime_weather(lat, lon):
    try:
        # Visual Crossing API - More accurate for specific coordinates
        api_key = "6RMYZDP5D68P5D4H9Q8UX7N9F" # Ye key active hai
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?unitGroup=metric&key={api_key}&contentType=json"
        response = requests.get(url, timeout=5).json()
        return round(float(response['currentConditions']['temp']), 1)
    except:
        return 35.0

# --- GPS JAVASCRIPT (Enhanced Accuracy) ---
st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                key: 'gps_coords',
                value: [pos.coords.latitude, pos.coords.longitude]
            }, '*');
        },
        (err) => { console.log(err); },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
    </script>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

# Session State
if 'gps_coords' not in st.session_state:
    st.session_state.gps_coords = [22.72, 71.64] # Surendranagar default
if 'temp_val' not in st.session_state:
    st.session_state.temp_val = 35.0

lat, lon = st.session_state.gps_coords

# --- INPUT SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    # Google Sheet data loading yahan aayega (aapki purani SHEET_ID ke saath)
    L = st.number_input("Tension Length (L)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Current Temp (°C)", value=st.session_state.temp_val, step=0.1)
    if st.button("🔄 Auto-Fetch Live"):
        st.session_state.temp_val = get_realtime_weather(lat, lon)
        st.rerun()

# --- CALCULATIONS & RESULTS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

st.markdown(f"<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
