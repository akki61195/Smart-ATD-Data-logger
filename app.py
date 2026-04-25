import streamlit as st
import pandas as pd
import requests
from streamlit_javascript import st_javascript

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 36px !important; }
    .stButton>button { background-color: #00d4ff !important; color: black !important; font-weight: bold !important; width: 100% !important; height: 3.5em !important; border-radius: 10px !important; }
    .status-box { padding: 12px; background-color: #1c2128; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; font-weight: bold; margin-bottom: 10px; text-align: center; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE RELIABLE GIS FETCH ---
def get_coords():
    # Ye JS seedha mobile browser se GIS data nikalega
    js_code = "navigator.geolocation.getCurrentPosition((pos) => { return pos.coords; });"
    loc = st_javascript("""navigator.geolocation.getCurrentPosition(
        pos => { window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'location', value: {lat: pos.coords.latitude, lon: pos.coords.longitude}}, '*'); },
        err => { console.error(err); }
    );""")
    return st.session_state.get('location')

def get_weather(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(w_url, timeout=5).json()
        temp = round(float(res['current_weather']['temperature']), 1)
        return temp
    except: return 35.0

# --- 4. UI & DATA ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0

# --- 5. INPUTS ---
L = st.number_input("Enter Tension Length (L)", value=750.0)

if st.button("🛰️ SYNC WITH PORTAL GIS"):
    # Force browser to run JS
    st_javascript("navigator.geolocation.getCurrentPosition(pos => { window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'location', value: {lat: pos.coords.latitude, lon: pos.coords.longitude}}, '*'); });")
    
    loc = st.session_state.get('location')
    if loc:
        with st.spinner('Fetching local temp...'):
            st.session_state.temp_val = get_weather(loc['lat'], loc['lon'])
            st.success(f"Linked to GIS: {loc['lat']}, {loc['lon']}")
    else:
        st.error("Browser ne location share nahi ki. Please check settings.")

theta_2 = st.number_input("🌡️ Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# --- 6. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("---")
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
