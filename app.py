import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. HIGH-VISIBILITY CSS (Professional Look) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    
    /* Input Labels */
    label p { color: #00d4ff !important; font-weight: bold !important; font-size: 1.1rem !important; }
    
    /* Metrics Box */
    div[data-testid="stMetric"] {
        background-color: #10161d !important;
        border: 1px solid #30363d !important;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #00ff41 !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }
    
    /* Info Box for Length */
    .status-box {
        padding: 15px;
        background-color: #1c2128;
        border: 1px solid #00d4ff;
        border-radius: 8px;
        color: #00d4ff !important;
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 18px;
    }

    /* Fixed Footer */
    .footer-credit {
        position: fixed; left: 0; bottom: 0; width: 100%;
        text-align: center; padding: 10px; font-size: 11px;
        background-color: #050a0f; color: #ffffff;
        border-top: 1px solid #30363d; z-index: 100;
    }

    .stButton>button { background-color: #00d4ff; color: black; font-weight: bold; width: 100%; border-radius: 8px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & WEATHER FUNCTIONS ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

def get_area_weather():
    try:
        # Detect Current Area (Wherever you are)
        geo_r = requests.get("http://ip-api.com/json/", timeout=3).json()
        lat, lon, city = geo_r['lat'], geo_r['lon'], geo_r['city']
        
        # Fetch Local Temp
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_r = requests.get(w_url, timeout=5).json()
        temp = round(float(w_r['current_weather']['temperature']), 1)
        return temp, city
    except:
        return 35.0, "Manual"

# --- 4. UI START ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

df = load_data()

if 'temp_val' not in st.session_state:
    st.session_state.temp_val = 35.0
if 'loc_name' not in st.session_state:
    st.session_state.loc_name = "Not Detected"

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
            L = st.number_input("Enter Length (L)", value=750.0)
    else:
        L = st.number_input("Enter Length (L)", value=750.0)

with col2:
    theta_2 = st.number_input("🌡️ Temp (°C)", value=st.session_state.temp_val, step=0.1)
    if st.button("🔄 Auto-Fetch Temp"):
        with st.spinner('Checking...'):
            new_t, city = get_area_weather()
            st.session_state.temp_val = new_t
            st.session_state.loc_name = city
            st.rerun()
    st.caption(f"📍 Area: {st.session_state.loc_name}")

# --- 6. CALCULATIONS ---
# Standard temp = 35, Alpha = 0.000017
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val = 1300 + delta
y_val = 2300 + (3 * delta)

# --- 7. OUTPUT ---
st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

# --- 8. FOOTER ---
st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
