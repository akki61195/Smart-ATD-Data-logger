import streamlit as st
import pandas as pd
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

# --- 2. DATA LOADING ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_sheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# --- 3. ADVANCED WEATHER ENGINE ---
def get_weather_by_coords(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        return round(float(w_res['current_weather']['temperature']), 1)
    except: return 35.0

def get_manual_city_data(city_name):
    try:
        # City name se Lat/Lon nikalna
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        res = requests.get(geo_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
        if res:
            lat, lon = res[0]['lat'], res[0]['lon']
            temp = get_weather_by_coords(lat, lon)
            return temp, res[0]['display_name']
        return 35.0, "City Not Found"
    except: return 35.0, "Network Error"

# --- 4. UI INITIALIZATION ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "GPS Not Active"

df = load_sheet_data()

# --- 5. STRUCTURE & LENGTH DISPLAY (Bigger Font) ---
if df is not None:
    struct_list = df['Structure_No'].dropna().unique().tolist()
    selected_struct = st.selectbox("📍 Select Structure No", ["Manual Entry"] + struct_list)
    if selected_struct != "Manual Entry":
        L = float(df[df['Structure_No'] == selected_struct]['Tension_Length'].values[0])
        st.markdown(f"<div class='length-display'>Tension Length (L): {L} m</div>", unsafe_allow_html=True)
    else: L = st.number_input("Enter Tension Length (L) manually", value=750.0)
else: L = st.number_input("Enter Tension Length (L) manually", value=750.0)

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
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current_weather=true"
                w_res = requests.get(w_url, timeout=5).json()
                st.session_state.temp_val = round(float(w_res['current_weather']['temperature']), 1)

                g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={location['latitude']}&lon={location['longitude']}"
                g_res = requests.get(g_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
                st.session_state.area_name = g_res.get('display_name', 'Local Section')

# --- 7. DISPLAY & RESULTS ---
st.markdown(f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
""", unsafe_allow_html=True)

theta_2 = st.number_input("Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Calculation Logic (35°C Standard)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.divider()
c1, c2 = st.columns(2)
c1.metric("X (Pulley Gap)", f"{round(x_val, 1)} mm")
c2.metric("Y (Weight Height)", f"{round(y_val, 1)} mm")


import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- HIGH QUALITY IMAGE CARD GENERATOR ---

curr_dt = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")

# 1. Image Quality Increase (Super Sampling 2x for HD Sharp Text)
scale = 2
width, height = 900 * scale, 550 * scale
img = Image.new("RGB", (width, height), color="#050a0f")
draw = ImageDraw.Draw(img)

# Font Sizing for High Resolution
try:
    font_title = ImageFont.truetype("arial.ttf", 36 * scale)
    font_body = ImageFont.truetype("arial.ttf", 24 * scale)
    font_val = ImageFont.truetype("arial.ttf", 30 * scale)
except IOError:
    font_title = font_body = font_val = ImageFont.load_default()

# Outer Border & Title Header
draw.rectangle([15 * scale, 15 * scale, width - 15 * scale, height - 15 * scale], outline="#00d4ff", width=4 * scale)
draw.text((35 * scale, 35 * scale), "⚡ OHE ATD SMART TOOL RECORD", fill="#00d4ff", font=font_title)
draw.line([(35 * scale, 90 * scale), (width - 35 * scale, 90 * scale)], fill="#00d4ff", width=2 * scale)

# Data Content
lines = [
    f"📅 Date & Time: {curr_dt}",
    f"📍 Location / Section: {st.session_state.area_name[:40]}",
    f"📏 Tension Length (L): {L} m",
    f"🌡️ Temperature: {theta_2} °C",
]

y_off = 120 * scale
for line in lines:
    draw.text((35 * scale, y_off), line, fill="#ffffff", font=font_body)
    y_off += 45 * scale

# X & Y Output Box
draw.rectangle([35 * scale, 340 * scale, width - 35 * scale, 500 * scale], fill="#1c2128", outline="#00ff41", width=3 * scale)
draw.text((60 * scale, 365 * scale), f"Calculated X Value : {x_val:.0f} mm", fill="#00ff41", font=font_val)
draw.text((60 * scale, 430 * scale), f"Calculated Y Value : {y_val:.0f} mm", fill="#00ff41", font=font_val)

# PNG Buffer Export
buf = io.BytesIO()
img.save(buf, format="PNG", optimize=True)

# --- 2. CENTERED BUTTON WITH CUSTOM STYLING ---
st.markdown("""
    <style>
    div[data-testid="stDownloadButton"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #002b49 !important; /* Dark Blue */
        color: #ccff00 !important;             /* Lime Yellow/Green */
        border: 2px solid #00d4ff !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 220px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #004070 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.download_button(
    label="💾 SAVE IMG",
    data=buf.getvalue(),
    file_name=f"ATD_Record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
    mime="image/png"
)

st.markdown(f"<div style='text-align: center; font-size: 10px; margin-top: 40px; opacity: 0.6;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
