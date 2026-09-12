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
    
    /* Tension Length (L) ka size bada karne ke liye */
    .length-display {
        font-size: 22px !important;
        font-weight: bold;
        color: #00ff41;
        padding: 10px;
        background: #1c2128;
        border-radius: 8px;
        border-left: 5px solid #00ff41;
        margin: 10px 0px;
    }
    
   div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 32px !important; }
    
   .stButton>button {
       background-color: #00d4ff !important;
       color: black !important;
@@ -31,7 +45,7 @@
   </style>
   """, unsafe_allow_html=True)

# --- 2. DATA LOADING (Google Sheet) ---
# --- 2. DATA LOADING ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@@ -56,7 +70,7 @@
area = g_res.get('display_name', 'Local Section Detected')
return temp, area
except:
        return 35.0, "Network Error (Manual Entry Mode)"
        return 35.0, "Network Error"

# --- 4. UI INITIALIZATION ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)
@@ -66,33 +80,42 @@

df = load_sheet_data()

# --- 5. STRUCTURE SELECTION ---
# --- 5. STRUCTURE & LENGTH DISPLAY ---
if df is not None:
struct_list = df['Structure_No'].dropna().unique().tolist()
selected_struct = st.selectbox("📍 Select Structure No", ["Manual Entry"] + struct_list)

if selected_struct != "Manual Entry":
L = float(df[df['Structure_No'] == selected_struct]['Tension_Length'].values[0])
        st.info(f"Tension Length (L) for {selected_struct}: **{L} m**")
        # Yahan size bada kar diya hai
        st.markdown(f"<div class='length-display'>Tension Length (L): {L} m</div>", unsafe_allow_html=True)
else:
L = st.number_input("Enter Tension Length (L) manually", value=750.0)
else:
    st.error("Google Sheet load nahi ho rahi. Check connectivity.")
L = st.number_input("Enter Tension Length (L) manually", value=750.0)

st.divider()

# --- 6. GPS & WEATHER SYNC ---
st.write("🛰️ Step 1: GPS Lock")
location = streamlit_geolocation()
# --- 6. LOCATION MODE SELECTION ---
manual_loc = st.checkbox("✍️ Enter Location Manually")

if location and location.get('latitude'):
    if st.button("🌡️ STEP 2: SYNC AREA & LIVE TEMP"):
        with st.spinner('Accessing local tower...'):
            t, a = get_full_data(location['latitude'], location['longitude'])
            st.session_state.temp_val = t
            st.session_state.area_name = a
            st.success("✅ Data Updated!")
if manual_loc:
    # Manual Entry Mode
    custom_area = st.text_input("Enter City/Location Name", value="Kodinar")
    st.session_state.area_name = custom_area
    st.caption("Manual mode active. Temperature override enabled.")
else:
    # GPS Mode
    st.write("🛰️ Step 1: GPS Lock")
    location = streamlit_geolocation()

    if location and location.get('latitude'):
        if st.button("🌡️ STEP 2: SYNC AREA & LIVE TEMP"):
            with st.spinner('Accessing local tower...'):
                t, a = get_full_data(location['latitude'], location['longitude'])
                st.session_state.temp_val = t
                st.session_state.area_name = a
                st.success("✅ Data Updated!")

# --- 7. DISPLAY AREA & RESULTS ---
st.markdown(f"""
@@ -102,7 +125,7 @@
   </div>
""", unsafe_allow_html=True)

theta_2 = st.number_input("🌡️ Working Temp (°C)", value=st.session_state.temp_val, step=0.1)
theta_2 = st.number_input("Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Logic using 35°C as standard reference
delta = L * 0.000017 * (35 - theta_2) * 1000
