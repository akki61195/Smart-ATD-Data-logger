import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import get_geolocation

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. MOBILE OPTIMIZED CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 36px !important; }
    
    .stButton>button {
        background-color: #00d4ff !important;
        color: #000000 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 10px !important;
        font-size: 18px !important;
    }
    
    .status-box { padding: 12px; background-color: #1c2128; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; font-weight: bold; margin-bottom: 10px; text-align: center; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. WEATHER ENGINE ---
def get_live_weather(lat, lon):
    try:
        # Get Area Name
        geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'ATD_Tool_V5'}
        geo_res = requests.get(geo_url, headers=headers, timeout=5).json()
        address = geo_res.get('address', {})
        area = address.get('city') or address.get('town') or address.get('village') or address.get('district') or "Trackside"
        
        # Get Temp
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        temp = round(float(w_res['current_weather']['temperature']), 1)
        return temp, area
    except:
        return 35.0, "Manual Check"

# --- 4. DATA LOADING ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# --- 5. UI CONSTRUCTION ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)
df = load_data()

# Initialize Session States
if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "GPS Not Active"

# --- 6. INPUTS ---
if df is not None:
    structs = df['Structure_No'].dropna().unique().tolist()
    selected = st.selectbox("📍 Structure No", ["Manual Entry"] + structs)
    if selected != "Manual Entry":
        L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
        st.markdown(f"<div class='status-box'>Tension Length: {L} m</div>", unsafe_allow_html=True)
    else: L = st.number_input("Enter Length (L)", value=750.0)
else: L = st.number_input("Enter Length (L)", value=750.0)

# --- 7. THE FIX: STABLE GPS BUTTON ---
if st.button("🛰️ AUTO-FETCH LOCATION & TEMP"):
    loc = get_geolocation() # Ye seedha mobile se permission maangega
    if loc:
        with st.spinner('Fetching Weather...'):
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            new_t, new_a = get_live_weather(lat, lon)
            st.session_state.temp_val = new_t
            st.session_state.area_name = new_a
            st.rerun()
    else:
        st.warning("Please allow location access in your browser settings (🔒 icon).")

theta_2 = st.number_input("🌡️ Current Temp (°C)", value=st.session_state.temp_val, step=0.1)
st.caption(f"📍 Area: {st.session_state.area_name}")

# --- 8. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("---")
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
