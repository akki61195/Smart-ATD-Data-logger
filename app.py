import streamlit as st
import pandas as pd
import requests
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP & CONFIGURATION ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp { 
        background-color: #050a0f; 
        color: white; 
    }
    .area-box { 
        padding: 15px; 
        background-color: #1c2128; 
        border: 2px solid #00d4ff; 
        border-radius: 12px; 
        text-align: center;
        margin: 15px 0px;
    }
    .area-label { 
        color: #00d4ff; 
        font-size: 14px; 
        margin-bottom: 2px; 
        font-weight: bold; 
    }
    .area-text { 
        font-size: 18px; 
        font-weight: bold; 
        color: #ffffff; 
    }
    .length-display {
        font-size: 24px !important;
        font-weight: bold;
        color: #00ff41;
        padding: 12px;
        background: #1c2128;
        border-radius: 8px;
        border-left: 8px solid #00ff41;
        margin: 10px 0px;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #00ff41 !important; 
        font-weight: 800; 
        font-size: 32px !important; 
    }
    .stButton>button {
        background-color: #00d4ff !important;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE INITIALIZATION ---
if "temp_val" not in st.session_state:
    st.session_state.temp_val = 35.0
if "area_name" not in st.session_state:
    st.session_state.area_name = "Not Selected / Manual Mode"

SHEET_URL = ""  # Add your CSV or Google Sheet URL here if available

@st.cache_data
def load_sheet_data():
    if not SHEET_URL:
        return None
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None

# --- 3. WEATHER & AREA ENGINE ---
def get_weather_by_coords(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        return round(float(w_res['current_weather']['temperature']), 1)
    except Exception:
        return 35.0

def get_manual_city_data(city_name):
    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        res = requests.get(geo_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
        if res:
            lat, lon = res[0]['lat'], res[0]['lon']
            temp = get_weather_by_coords(lat, lon)
            return temp, res[0]['display_name']
        return 35.0, "City Not Found"
    except Exception:
        return 35.0, "Network Error"

# --- 4. HEADER ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>⚡ OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

df = load_sheet_data()

# --- 5. STRUCTURE & LENGTH DISPLAY ---
if df is not None and 'Structure_No' in df.columns:
    struct_list = df['Structure_No'].dropna().unique().tolist()
    selected_struct = st.selectbox("📍 Select Structure No", ["Manual Entry"] + struct_list)
    
    if selected_struct != "Manual Entry":
        L = float(df[df['Structure_No'] == selected_struct]['Tension_Length'].values[0])
        st.markdown(f"<div class='length-display'>Tension Length (L): {L} m</div>", unsafe_allow_html=True)
    else:
        L = st.number_input("Enter Tension Length (L) manually", value=750.0)
else:
    L = st.number_input("Enter Tension Length (L) manually", value=750.0)

st.divider()

# --- 6. LOCATION MODE ---
manual_loc = st.checkbox("✍️ Enter Location Manually")

if manual_loc:
    city_input = st.text_input("Enter City Name (e.g. Kodinar, Junagadh)", value="Kodinar")
    if st.button("🔍 FETCH TEMP FOR THIS CITY"):
        with st.spinner('Fetching data...'):
            t, a = get_manual_city_data(city_input)
            st.session_state.temp_val = t
            st.session_state.area_name = a
else:
    st.write("🛰️ GPS Mode")
    location = streamlit_geolocation()

    if location and location.get('latitude'):
        if st.button("🌡️ SYNC LIVE AREA & TEMP"):
            with st.spinner('Syncing...'):
                try:
                    lat, lon = location['latitude'], location['longitude']
                    t = get_weather_by_coords(lat, lon)
                    g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
                    g_res = requests.get(g_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
                    a = g_res.get('display_name', 'Local Section')
                    
                    st.session_state.temp_val = t
                    st.session_state.area_name = a
                    st.success("✅ Data Updated!")
                except Exception:
                    st.error("Failed to sync GPS data.")

# --- 7. DISPLAY & RESULTS ---
st.markdown(f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
""", unsafe_allow_html=True)

theta_2 = st.number_input("Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Calculation Logic (35°C Standard Reference)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val = 1300 + delta
y_val = 2300 + (3 * delta)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Calculated X Value", value=f"{x_val:.0f} mm")
with col2:
    st.metric(label="Calculated Y Value", value=f"{y_val:.0f} mm")
