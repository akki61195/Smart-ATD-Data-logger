import streamlit as st
import pandas as pd
import requests
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP & CONFIGURATION ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: white; }
    .area-box { 
        padding: 15px; background-color: #1c2128; border: 2px solid #00d4ff; 
        border-radius: 12px; text-align: center; margin: 15px 0px; 
    }
    .area-label { color: #00d4ff; font-size: 14px; margin-bottom: 2px; font-weight: bold; }
    .area-text { font-size: 18px; font-weight: bold; color: #ffffff; }
    .length-display {
        font-size: 20px !important; font-weight: bold; color: #00ff41; padding: 12px;
        background: #1c2128; border-radius: 8px; border-left: 6px solid #00ff41; margin: 10px 0px;
    }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 32px !important; }
    .stButton>button { background-color: #00d4ff !important; color: black !important; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE INITIALIZATION ---
if "temp_val" not in st.session_state:
    st.session_state.temp_val = 35.0
if "area_name" not in st.session_state:
    st.session_state.area_name = "Not Selected / Manual Mode"

# --- 3. GOOGLE SHEET / CSV INPUT (FEATURE 1) ---
st.sidebar.header("⚙️ Data Source & Sheet")
sheet_url_input = st.sidebar.text_input("📊 Enter CSV / Google Sheet Link", value="")

@st.cache_data
def load_sheet_data(url):
    if not url:
        return None
    try:
        # Convert Google Sheet view link to CSV export link if needed
        if "docs.google.com/spreadsheets" in url and "export?format=csv" not in url:
            url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading sheet: {e}")
        return None

# --- 4. WEATHER & LOCATION ENGINE (FEATURE 2) ---
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

# --- 5. HEADER ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>⚡ OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

# Load Sheet
df = load_sheet_data(sheet_url_input)

# --- 6. STRUCTURE LOCATION & TENSION LENGTH (CSV FEATURE) ---
st.subheader("📍 Structure Location & Tension Length")

if df is not None:
    # Try finding Structure Column
    struct_col = [c for c in df.columns if 'struct' in c.lower() or 'loc' in c.lower()]
    length_col = [c for c in df.columns if 'length' in c.lower() or 'tension' in c.lower() or c.lower() == 'l']
    
    if struct_col and length_col:
        struct_col_name = struct_col[0]
        length_col_name = length_col[0]
        
        struct_list = df[struct_col_name].dropna().astype(str).unique().tolist()
        selected_struct = st.selectbox("Select Structure No / Location from CSV:", ["Manual Entry"] + struct_list)
        
        if selected_struct != "Manual Entry":
            L = float(df[df[struct_col_name].astype(str) == selected_struct][length_col_name].values[0])
            st.markdown(f"<div class='length-display'>✅ Tension Length (L) from Sheet: {L} m</div>", unsafe_allow_html=True)
        else:
            L = st.number_input("Enter Tension Length (L) manually (meters)", value=750.0)
    else:
        st.warning("⚠️ Sheet detected, but 'Structure_No' or 'Tension_Length' columns missing.")
        L = st.number_input("Enter Tension Length (L) manually (meters)", value=750.0)
else:
    st.info("ℹ️ Enter CSV / Google Sheet Link in the sidebar to auto-fetch Structure Location & Length.")
    L = st.number_input("Enter Tension Length (L) manually (meters)", value=750.0)

st.divider()

# --- 7. GPS LOCATION & TEMP FETCH ---
st.subheader("🛰️ GPS Location & Temperature Fetch")

location = streamlit_geolocation()

col_gps, col_city = st.columns(2)

with col_gps:
    if location and location.get('latitude'):
        if st.button("🌡️ FETCH TEMP FROM GPS"):
            with st.spinner('Fetching GPS Temperature...'):
                try:
                    lat, lon = location['latitude'], location['longitude']
                    t = get_weather_by_coords(lat, lon)
                    g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
                    g_res = requests.get(g_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
                    a = g_res.get('display_name', 'GPS Location Detected')
                    
                    st.session_state.temp_val = t
                    st.session_state.area_name = a
                    st.success("✅ GPS Data Fetched!")
                except Exception:
                    st.error("Error fetching GPS data.")

with col_city:
    with st.expander("✍️ Search Temp by City"):
        city_input = st.text_input("City Name", value="Kodinar")
        if st.button("🔍 SEARCH CITY TEMP"):
            with st.spinner('Searching...'):
                t, a = get_manual_city_data(city_input)
                st.session_state.temp_val = t
                st.session_state.area_name = a
                st.success("✅ City Temp Fetched!")

# --- 8. DISPLAY & RESULTS ---
st.markdown(f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE LOCATION / SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
""", unsafe_allow_html=True)

theta_2 = st.number_input("Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Calculation Logic (35°C Standard Reference)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val = 1300 + delta
y_val = 2300 + (3 * delta)

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="Calculated X Value", value=f"{x_val:.0f} mm")
with res_col2:
    st.metric(label="Calculated Y Value", value=f"{y_val:.0f} mm")
