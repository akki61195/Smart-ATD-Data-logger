import streamlit as st
import pandas as pd
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="🌡️", layout="centered")

# --- CUSTOM CSS ---
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
    .status-box {
        padding: 10px; border-radius: 8px;
        background-color: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        margin-bottom: 20px;
    }
    .footer-credit {
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; padding: 10px; font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING (Google Sheet) ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip() 
        return df
    except:
        return None

# --- FUNCTION: FETCH TEMP FROM OPEN-METEO ---
def get_openmeteo_temp(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        return round(float(response['current_weather']['temperature']), 1)
    except:
        return 35.0

# --- GPS JAVASCRIPT ---
st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                key: 'gps_coords',
                value: [position.coords.latitude, position.coords.longitude]
            }, '*');
        }
    );
    </script>
""", unsafe_allow_html=True)

# --- MAIN APP ---
st.markdown("<h2 style='text-align: center;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

df = load_data()

# Location & Temp Handling
if 'gps_coords' not in st.session_state:
    st.session_state.gps_coords = [22.72, 71.64] # Default Surendranagar

lat, lon = st.session_state.gps_coords
live_temp = get_openmeteo_temp(lat, lon)

# --- INPUT SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    if df is not None:
        struct_list = df['Structure_No'].dropna().unique().tolist()
        selected_struct = st.selectbox("📍 Structure Number", ["Manual Entry"] + struct_list)
        
        if selected_struct != "Manual Entry":
            L = float(df[df['Structure_No'] == selected_struct]['Tension_Length'].values[0])
            st.markdown(f"<div class='status-box'>Tension Length: {L} m</div>", unsafe_allow_html=True)
        else:
            L = st.number_input("Manual Tension Length (L)", value=750.0)
    else:
        L = st.number_input("Tension Length (L)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Current Temp (°C)", value=live_temp, step=0.1)
    st.caption(f"📍 GPS Sync: {round(lat,2)}, {round(lon,2)}")

# --- CALCULATIONS ---
alpha, theta_1 = 0.000017, 35
delta_1 = L * alpha * (theta_1 - theta_2) * 1000
x_val, y_val = 1300 + delta_1, 2300 + (3 * delta_1)

# --- RESULTS ---
st.divider()
st.write("#### Technical Output")
r1, r2 = st.columns(2)
r1.metric("X Value (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta_1, 1)} mm")
r2.metric("Y Value (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta_1, 1)} mm")

# --- FOOTER ---
st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
