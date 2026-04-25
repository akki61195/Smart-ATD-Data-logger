import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: white; }
    .area-box { 
        padding: 15px; 
        background-color: #1c2128; 
        border: 2px solid #00d4ff; 
        border-radius: 12px; 
        text-align: center;
        margin: 15px 0px;
    }
    .area-label { color: #00d4ff; font-size: 14px; margin-bottom: 2px; font-weight: bold; }
    .area-text { font-size: 18px; font-weight: bold; color: #ffffff; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 32px !important; }
    .stButton>button {
        background-color: #00d4ff !important;
        color: black !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. WEATHER & AREA ENGINE ---
def get_full_data(lat, lon):
    try:
        # Weather Fetch
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        temp = round(float(w_res['current_weather']['temperature']), 1)
        
        # Area Name Fetch (OpenStreetMap)
        g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        g_res = requests.get(g_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
        area = g_res.get('display_name', 'Local Section Detected')
        return temp, area
    except:
        return 35.0, "Network Error (Manual Entry Required)"

# --- 3. UI INITIALIZATION ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "GPS Not Active"

# --- 4. STEP 1: GPS LOCK ---
st.info("📍 Step 1: Click button and 'Allow' for GPS Lock")
location = streamlit_geolocation()

# --- 5. STEP 2: SYNC WEATHER & AREA ---
if location and location.get('latitude'):
    if st.button("🌡️ STEP 2: FETCH LIVE AREA & TEMP"):
        with st.spinner('Accessing local tower...'):
            t, a = get_full_data(location['latitude'], location['longitude'])
            st.session_state.temp_val = t
            st.session_state.area_name = a
            st.success("✅ Sync Complete!")

# --- 6. DISPLAY AREA BOX (Jaisa aapne manga tha) ---
st.markdown(f"""
    <div class="area-box">
        <div class="area-label">📡 DETECTED SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
""", unsafe_allow_html=True)

# --- 7. INPUTS & CALCULATION ---
L = st.number_input("Tension Length (L) in meters", value=750.0, step=1.0)
theta_2 = st.number_input("🌡️ Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Logic using 35°C as standard reference
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.divider()
c1, c2 = st.columns(2)
c1.metric("X (Pulley Gap)", f"{round(x_val, 1)} mm")
c2.metric("Y (Weight Height)", f"{round(y_val, 1)} mm")

st.markdown(f"<div style='text-align: center; font-size: 10px; margin-top: 40px; opacity: 0.6;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
