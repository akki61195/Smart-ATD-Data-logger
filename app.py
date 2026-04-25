import streamlit as st
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Location Area Sync", page_icon="📍")

# Custom CSS for Mobile UI
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: white; }
    .big-font { font-size: 24px !important; font-weight: bold; color: #00d4ff; }
    .area-box { 
        padding: 20px; 
        background-color: #1c2128; 
        border: 2px solid #00d4ff; 
        border-radius: 15px; 
        margin: 10px 0px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        height: 4em;
        background-color: #00d4ff !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. JAVASCRIPT TRIGGER ---
# Button click par ye JS chalega aur seedha Streamlit state mein data daalega
def trigger_gps_js():
    js_code = """
    <script>
    async function fetchGPS() {
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                
                // Area Name Fetch (OpenStreetMap)
                try {
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                    const data = await response.json();
                    const areaName = data.display_name;
                    
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        key: 'final_gps',
                        value: { lat: lat, lon: lon, area: areaName }
                    }, '*');
                } catch (e) {
                    console.error("Area fetch failed");
                }
            },
            (err) => { alert("Please enable GPS/Location on your phone."); },
            { enableHighAccuracy: true }
        );
    }
    fetchGPS();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. MAIN UI ---
st.markdown("<div class='big-font'>🛰️ OHE Location Sync</div>", unsafe_allow_html=True)
st.write("Section verify karne ke liye niche wala button dabayein.")

# Action Button
if st.button("📍 DETECT MY CURRENT AREA"):
    trigger_gps_js()

# Data Display logic
gps_info = st.session_state.get('final_gps')

if gps_info:
    st.markdown(f"""
        <div class="area-box">
            <p style="color: #00d4ff; font-size: 14px; margin-bottom: 5px;">CURRENT SECTION</p>
            <p style="font-size: 20px; font-weight: bold;">{gps_info['area']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("Lat", f"{gps_info['lat']:.5f}")
    col2.metric("Lon", f"{gps_info['lon']:.5f}")
    
    st.success("✅ GPS Lock Successful")
else:
    st.info("Waiting for input... Button dabane ke baad 'Allow' click karein.")

st.divider()
st.caption("Phase 1.2: Mobile Hardware Sync | JE/TRD Mulchandani")
