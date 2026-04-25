import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800 !important; }
    .status-box { padding: 15px; background-color: #161b22; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; font-weight: bold; margin-bottom: 10px; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    .stButton>button { background-color: #00d4ff; color: black; font-weight: bold; width: 100%; height: 3em; border-radius: 8px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DYNAMIC GPS SCRIPT ---
# Ye script browser se live coordinates lega
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
        (err) => { console.log("GPS Error"); },
        { enableHighAccuracy: true }
    );
    </script>
""", unsafe_allow_html=True)

# --- 4. DATA & WEATHER FUNCTIONS ---
def get_live_data(lat, lon):
    try:
        # Step 1: Area Name (Reverse Geocoding)
        geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'ATD_Smart_Tool_V2'}
        geo_res = requests.get(geo_url, headers=headers, timeout=5).json()
        address = geo_res.get('address', {})
        # Junagadh, Mumbai ya koi bhi area detect hoga
        area = address.get('city') or address.get('town') or address.get('district') or address.get('county') or "Unknown Area"
        
        # Step 2: Live Temperature
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        temp = round(float(w_res['current_weather']['temperature']), 1)
        
        return temp, area
    except:
        return 35.0, "Manual Entry Required"

# Google Sheet Connection
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# --- 5. UI LOGIC ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

df = load_data()

# Initialize session states if not present
if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'loc_display' not in st.session_state: st.session_state.loc_display = "Waiting for GPS..."

# --- 6. INPUTS ---
col1, col2 = st.columns([1.5, 1])

with col1:
    if df is not None:
        structs = df['Structure_No'].dropna().unique().tolist()
        selected = st.selectbox("📍 Structure No", ["Manual Entry"] + structs)
        if selected != "Manual Entry":
            L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
            st.markdown(f"<div class='status-box'>Tension Length: {L} m</div>", unsafe_allow_html=True)
        else: L = st.number_input("Enter Length (L)", value=750.0)
    else: L = st.number_input("Enter Length (L)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Temp (°C)", value=st.session_state.temp_val, step=0.1)
    if st.button("🔄 Auto-Fetch"):
        if 'gps_coords' in st.session_state:
            with st.spinner('Locating...'):
                lat, lon = st.session_state.gps_coords
                new_t, new_a = get_live_data(lat, lon)
                st.session_state.temp_val = new_t
                st.session_state.loc_display = new_a
                st.rerun()
        else:
            st.warning("GPS not ready. Please allow location.")

st.caption(f"📍 Area: {st.session_state.loc_display}")

# --- 7. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
