import streamlit as st
import pandas as pd
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="🌡️", layout="centered")

# --- CUSTOM CSS (Dark Blue Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    .footer-credit {
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; padding: 10px; font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTION: FETCH TEMP FROM OPEN-METEO ---
def get_openmeteo_temp(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        temp = response['current_weather']['temperature']
        return round(float(temp), 1)
    except Exception as e:
        return 35.0 # Fallback temperature

# --- GPS JAVASCRIPT ---
# Browser se coordinate lene ke liye
st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                key: 'gps_coords',
                value: [lat, lon]
            }, '*');
        }
    );
    </script>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
st.markdown("<h2 style='text-align: center;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.7;'>GPS & Open-Meteo Integrated</p>", unsafe_allow_html=True)

# Location Data Handling
if 'gps_coords' not in st.session_state:
    # Default to Surendranagar coordinates if GPS not yet loaded
    st.session_state.gps_coords = [22.72, 71.64]

lat, lon = st.session_state.gps_coords
live_temp = get_openmeteo_temp(lat, lon)

# --- INPUT SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    L = st.number_input("Tension Length (L)", value=750.0, step=10.0)
    st.caption(f"📍 Current GPS: {lat}, {lon}")

with col2:
    theta_2 = st.number_input("🌡️ Current Temp (°C)", value=live_temp, step=0.1)
    if st.button("🔄 Refresh Temp"):
        st.rerun()

# --- CALCULATIONS ---
alpha = 0.000017
theta_1 = 35 # Standard Temp
delta_1 = L * alpha * (theta_1 - theta_2) * 1000
x_val = 1300 + delta_1
y_val = 2300 + (3 * delta_1)

# --- RESULTS ---
st.markdown("---")
st.write("#### Technical Output")
r1, r2 = st.columns(2)
r1.metric("X Value (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta_1, 1)} mm")
r2.metric("Y Value (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta_1, 1)} mm")

# --- FOOTER ---
st.markdown(f"<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
