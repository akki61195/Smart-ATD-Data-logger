import streamlit as st
import pandas as pd
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="⚡", layout="centered")

# --- PROFESSIONAL THEME CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0d1117; /* Professional Dark Grey-Blue */
        color: #e6edf3;
    }
    
    /* Header Styling */
    h2 { color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Results Card - High Visibility */
    div[data-testid="stMetric"] {
        background-color: #161b22 !important;
        border: 2px solid #30363d !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }

    /* Metric Values Color */
    div[data-testid="stMetricValue"] > div {
        color: #3fb950 !important; /* Sharp Green for clarity */
        font-weight: bold !important;
    }

    /* Status Box for Tension Length */
    .status-box {
        padding: 12px;
        border-radius: 8px;
        background-color: rgba(88, 166, 255, 0.1);
        border: 1px solid #58a6ff;
        margin-bottom: 20px;
        color: #58a6ff;
        font-weight: 500;
    }

    /* Fixed Footer */
    .footer-credit {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 8px;
        font-size: 11px;
        background-color: #0d1117;
        color: #8b949e;
        border-top: 1px solid #30363d;
        letter-spacing: 1px;
    }

    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- DATA & WEATHER FUNCTIONS ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip() 
        return df
    except: return None

def get_openmeteo_temp(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        return round(float(response['current_weather']['temperature']), 1)
    except: return 35.0

# --- GPS SCRIPT ---
st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition((pos) => {
        window.parent.postMessage({
            type: 'streamlit:set_widget_value',
            key: 'gps_coords',
            value: [pos.coords.latitude, pos.coords.longitude]
        }, '*');
    });
    </script>
""", unsafe_allow_html=True)
