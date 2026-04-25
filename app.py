import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="⚡", layout="centered")

# --- 2. PROFESSIONAL DARK THEME (High Visibility) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Metrics Box - Ab ye dhoop mein bhi dikhega */
    div[data-testid="stMetric"] {
        background-color: #1c2128 !important;
        border: 1px solid #30363d !important;
        padding: 15px !important;
        border-radius: 10px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #4cd964 !important; /* Bright Neon Green */
        font-size: 28px !important;
    }
    
    .status-box {
        padding: 10px;
        background-color: rgba(88, 166, 255, 0.1);
        border: 1px solid #58a6ff;
        border-radius: 5px;
        margin-bottom: 15px;
    }

    .footer-credit {
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; padding: 10px; font-size: 11px;
        background-color: #0d1117; color: #8b949e;
        border-top: 1px solid #30363d;
    }
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

# --- 4. UI START ---
st.markdown("<h2 style='text-align: center;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

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
        selected = st.selectbox("📍 Structure No", ["Manual"] + structs)
        if selected != "Manual":
            L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
            st.markdown(f"<div class='status-box'>Length: {L} m</div>", unsafe_allow_html=True)
        else:
            L = st.number_input("Length (L)", value=750.0)
    else:
        L = st.number_input("Length (L)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Temp (°C)", value=st.session_state.temp_val, step=0.1)
    
    if st.button("🔄 Auto-Fetch"):
        # Simple location fetch
        st.session_state.temp_val = get_weather(st.session_state.lat, st.session_state.lon)
        st.rerun()

# --- 6. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

# --- 7. RESULTS ---
st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

# --- 8. FOOTER ---
st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
