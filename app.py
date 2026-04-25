import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="⚡", layout="centered")

# --- 2. HIGH-VISIBILITY PROFESSIONAL THEME ---
st.markdown("""
    <style>
    /* Pure Dark Background */
    .stApp {
        background-color: #050a0f !important;
        color: #ffffff !important;
    }

    /* Force ALL Labels to be Bright White */
    label, .stMarkdown, p, span, div {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* Make Input Titles bigger and Cyan */
    label p {
        color: #00d4ff !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    /* Metrics Card - High Contrast Border */
    div[data-testid="stMetric"] {
        background-color: #10161d !important;
        border: 2px solid #30363d !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }

    /* Metric Large Values */
    div[data-testid="stMetricValue"] > div {
        color: #00ff41 !important; /* Neon Green */
        font-size: 32px !important;
        font-weight: 800 !important;
    }

    /* Structure & Length Info Box */
    .status-box {
        padding: 15px;
        background-color: #1c2128;
        border: 1px solid #00d4ff;
        border-radius: 8px;
        color: #00d4ff !important;
        font-size: 18px;
        margin-bottom: 10px;
    }

    /* Footer Branding */
    .footer-credit {
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; padding: 10px; font-size: 12px;
        background-color: #050a0f; 
        color: #ffffff !important;
        border-top: 1px solid #30363d;
        z-index: 999;
    }

    /* Hide unnecessary elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & FUNCTIONS ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        r = requests.get(url, timeout=5).json()
        return round(float(r['current_weather']['temperature']), 1)
    except: return 35.0

# --- 4. MAIN INTERFACE ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

df = load_data()

# Location state (Default: Surendranagar)
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 22.72, 71.64
if 'temp_val' not in st.session_state:
    st.session_state.temp_val = 35.0

# --- 5. INPUT SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    if df is not None:
        structs = df['Structure_No'].dropna().unique().tolist()
        selected = st.selectbox("📍 Structure No", ["Manual Entry"] + structs)
        if selected != "Manual Entry":
            L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
            st.markdown(f"<div class='status-box'>Tension Length: {L} m</div>", unsafe_allow_html=True)
        else:
            L = st.number_input("Enter Length (m)", value=750.0)
    else:
        L = st.number_input("Enter Length (m)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Temp (°C)", value=st.session_state.temp_val, step=0.1)
    if st.button("🔄 Auto-Fetch Temp"):
        st.session_state.temp_val = get_weather(st.session_state.lat, st.session_state.lon)
        st.rerun()

# --- 6. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

# --- 7. RESULTS ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px; color: #ffffff;'>Calculated Values:</p>", unsafe_allow_html=True)
r1, r2 = st.columns(2)

r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

# --- 8. FOOTER ---
st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
