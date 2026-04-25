import streamlit as st
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. CSS (Clean & Dark Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 36px !important; }
    .stButton>button { background-color: #00d4ff !important; color: black !important; font-weight: bold !important; width: 100% !important; height: 3.5em !important; border-radius: 10px !important; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. WEATHER ENGINE ---
def get_weather_by_coords(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(w_url, timeout=5).json()
        temp = round(float(res['current_weather']['temperature']), 1)
        
        # Area name reverse geocoding
        geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        g_res = requests.get(geo_url, headers={'User-Agent': 'ATD_JE_Tool'}, timeout=5).json()
        area = g_res.get('address', {}).get('city') or g_res.get('address', {}).get('town') or "Local Site"
        
        return temp, area
    except:
        return 35.0, "Manual Set"

# --- 4. UI ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

# URL se lat/lon check karna (Portal Integration ke liye best)
params = st.query_params
lat_param = params.get("lat")
lon_param = params.get("lon")

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "Not Synced"

# --- 5. INPUTS ---
L = st.number_input("Tension Length (L) in meters", value=750.0, step=1.0)

# Agar URL mein data nahi hai toh manual trigger
if st.button("🛰️ SYNC WITH LOCAL WEATHER"):
    # Sabse stable IP API use kar rahe hain (Dallas se bachne ke liye logic ke saath)
    with st.spinner('Accessing Regional Tower...'):
        try:
            # Browser IP bypass using a different provider
            ip_data = requests.get('https://ipapi.co/json/', timeout=5).json()
            if ip_data.get('country_code') == 'IN': # Sirf India ka data allow karega
                st.session_state.temp_val, st.session_state.area_name = get_weather_by_coords(ip_data['latitude'], ip_data['longitude'])
                st.rerun()
            else:
                st.error("Dallas (USA) detect ho raha hai. Please use Mobile Hotspot or Manual Entry.")
        except:
            st.error("Network issue. Please enter temperature manually.")

theta_2 = st.number_input("🌡️ Working Temp (°C)", value=st.session_state.temp_val, step=0.1)
st.caption(f"📍 Location: {st.session_state.area_name}")

# --- 6. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("---")
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm")

st.markdown(f"<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
