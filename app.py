import streamlit as st
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. PROFESSIONAL RAILWAY CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 36px !important; }
    .stButton>button { 
        background-color: #00d4ff !important; 
        color: black !important; 
        font-weight: bold !important; 
        width: 100% !important; 
        height: 3.8em !important; 
        border-radius: 12px !important; 
    }
    .status-box { padding: 15px; background-color: #1c2128; border: 1px solid #30363d; border-radius: 8px; color: #00d4ff !important; margin-bottom: 15px; text-align: center; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTO-LOCATION ENGINE (NO GIS REQUIRED) ---
def fetch_auto_data():
    try:
        # IP Address se location track karna
        response = requests.get('http://ip-api.com/json/', timeout=5).json()
        if response['status'] == 'success':
            lat = response['lat']
            lon = response['lon']
            city = response['city']
            
            # Use coordinates for Weather
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            w_res = requests.get(w_url, timeout=5).json()
            temp = round(float(w_res['current_weather']['temperature']), 1)
            return temp, city
        return None, None
    except:
        return None, None

# --- 4. DATA LOADING (GOOGLE SHEET) ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# --- 5. MAIN UI ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)
df = load_data()

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "Not Synced"

# --- 6. TOWER & STRUCTURE SELECTION ---
if df is not None:
    structs = df['Structure_No'].dropna().unique().tolist()
    selected = st.selectbox("📍 Select Structure No (Master Data)", ["Manual Entry"] + structs)
    if selected != "Manual Entry":
        L = float(df[df['Structure_No'] == selected]['Tension_Length'].values[0])
        st.markdown(f"<div class='status-box'>Tension Length (L): {L} m</div>", unsafe_allow_html=True)
    else: L = st.number_input("Enter Length (L) Manually", value=750.0)
else:
    L = st.number_input("Enter Length (L)", value=750.0)

# --- 7. THE "NO-GIS" BUTTON ---
if st.button("🛰️ AUTO-SYNC FROM PORTAL SIGNAL"):
    with st.spinner('Syncing with local tower...'):
        t, c = fetch_auto_data()
        if t:
            st.session_state.temp_val = t
            st.session_state.area_name = c
            st.rerun()
        else:
            st.error("Network Signal Weak! Please check portal connection.")

# --- 8. RESULTS ---
theta_2 = st.number_input("🌡️ Working Temp (°C)", value=st.session_state.temp_val, step=0.1)
st.caption(f"📍 Signal Area: {st.session_state.area_name}")

delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("<br>", unsafe_allow_html=True)
r1, r2 = st.columns(2)
r1.metric("X (Pulley Gap)", f"{round(x_val, 1)} mm", f"{round(delta, 1)} mm")
r2.metric("Y (Weight Height)", f"{round(y_val, 1)} mm", f"{round(3*delta, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
