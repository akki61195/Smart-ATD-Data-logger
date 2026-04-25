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
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 32px !important; }
    .status-box { padding: 15px; background-color: #1c2128; border: 1px solid #00d4ff; border-radius: 8px; color: #00d4ff !important; font-weight: bold; margin-bottom: 10px; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    .stButton>button { background-color: #00d4ff; color: black; font-weight: bold; width: 100%; border-radius: 8px; height: 3.5em; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GPS ACTIVATOR SCRIPT ---
# Ye function sirf tab chalega jab button dabaya jayega
def trigger_gps():
    gps_script = """
    <script>
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                key: 'gps_data',
                value: {lat: pos.coords.latitude, lon: pos.coords.longitude}
            }, '*');
        },
        (err) => { alert("Please enable Location in Browser Settings (🔒 icon next to URL)"); },
        { enableHighAccuracy: true }
    );
    </script>
    """
    st.components.v1.html(gps_script, height=0)

# --- 4. WEATHER & DATA FUNCTIONS ---
def get_live_weather(lat, lon):
    try:
        # Area Name
        geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'ATD_Smart_Tool_Final'}
        geo_res = requests.get(geo_url, headers=headers, timeout=5).json()
        address = geo_res.get('address', {})
        area = address.get('city') or address.get('town') or address.get('village') or address.get('district') or "Field"
        
        # Temp
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        temp = round(float(w_res['current_weather']['temperature']), 1)
        return temp, area
    except:
        return 35.0, "Unknown"

SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# --- 5. UI ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)
df = load_data()

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "GPS Not Active"

# --- 6. INPUTS ---
col1, col2 = st.columns([1.5, 1])

with col1:
    if df is not None:
        structs = df['Structure_No'].dropna().unique().tolist()
        selected = st.selectbox("📍 Structure No", ["Manual Entry"] + structs)
        if selected != "Manual Entry":
            L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
            st.markdown(f"<div class='status-box'>Length: {L} m</div>", unsafe_allow_html=True)
        else: L = st.number_input("Length (L)", value=750.0)
    else: L = st.number_input("Length (L)", value=750.0)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🛰️ Activate GPS & Fetch"):
        trigger_gps() # Pehle permission trigger karega
        if 'gps_data' in st.session_state:
            with st.spinner('Detecting Area...'):
                lat, lon = st.session_state.gps_data['lat'], st.session_state.gps_data['lon']
                new_t, new_a = get_live_weather(lat, lon)
                st.session_state.temp_val = new_t
                st.session_state.area_name = new_a
                st.rerun()

    theta_2 = st.number_input("🌡️ Temp (°C)", value=st.session_state.temp_val, step=0.1)

st.caption(f"📍 Area: {st.session_state.area_name}")

# --- 7. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
