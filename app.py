import streamlit as st
import requests
from streamlit_javascript import st_javascript

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE FETCH LOGIC ---
st.title("🛰️ OHE Location Sync")

# Ye JavaScript seedha mobile browser se GIS data nikalega
js_geo = "{lat: 0, lon: 0}; navigator.geolocation.getCurrentPosition((pos) => { window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'location', value: {lat: pos.coords.latitude, lon: pos.coords.longitude}}, '*'); });"

st.write("Section detect karne ke liye niche check karein.")

# JavaScript execution
loc = st_javascript("navigator.geolocation.getCurrentPosition(pos => { return {lat: pos.coords.latitude, lon: pos.coords.longitude}; });")

if loc and isinstance(loc, dict) and loc.get('lat') != 0:
    lat, lon = loc['lat'], loc['lon']
    
    # Area Name Fetching
    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}", headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
        area = res.get('display_name', 'Location found but name unavailable')
    except:
        area = "Connection Error (Area Name)"

    st.markdown(f"<div class='area-display'>{area}</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Latitude", round(lat, 5))
    c2.metric("Longitude", round(lon, 5))
    st.success("✅ GPS Data Synced Successfully")

else:
    st.warning("⏳ GPS signal ka intezar hai... Please 'Allow' permission click karein.")
    if st.button("🔄 Force Refresh Location"):
        st.rerun()

st.divider()
st.caption("Phase 1.3 | Hardware-Level Sync | JE/TRD Mulchandani")
