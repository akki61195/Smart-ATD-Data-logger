import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Railway Location Sync", page_icon="📍")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: white; }
    .area-display { 
        padding: 20px; 
        background-color: #1c2128; 
        border: 2px solid #00d4ff; 
        border-radius: 12px; 
        text-align: center;
        font-weight: bold;
        color: #00d4ff;
    }
    /* Button ko railway style mein bada karne ke liye */
    button[kind="secondary"] {
        background-color: #00d4ff !important;
        color: black !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 4em !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ OHE Location Sync")
st.write("Niche diye gaye button par click karke 'Allow' karein.")

# --- 2. THE COMPONENT ---
# Ye component ek pre-made button deta hai jo hardware access karta hai
location = streamlit_geolocation()

if location and location.get('latitude'):
    lat = location['latitude']
    lon = location['longitude']
    
    # Reverse Geocoding to get Area Name
    try:
        # User-Agent header zaroori hai Nominatim API ke liye
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        res = requests.get(url, headers={'User-Agent': 'RailwayATD_Tool'}, timeout=5).json()
        area = res.get('display_name', 'Location Detected')
    except:
        area = f"Coordinates: {lat}, {lon}"

    st.markdown(f"<div class='area-display'>📍 {area}</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Latitude", round(lat, 5))
    c2.metric("Longitude", round(lon, 5))
    st.success("✅ Phase 1 Complete: Location Synced!")

else:
    st.info("Waiting... Button dabane par Chrome aapse permission maangega.")

st.divider()
st.caption("Phase 1.4 | Component-Level Access | JE/TRD Mulchandani")
