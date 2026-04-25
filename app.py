import streamlit as st
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Location & Area Tester", page_icon="📍")

# --- 2. JAVASCRIPT FOR GPS & AREA ---
st.components.v1.html("""
<script>
    async function getAreaName(lat, lon) {
        try {
            // OpenStreetMap ki free API use kar rahe hain area naam ke liye
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
            const data = await response.json();
            return data.display_name;
        } catch (err) {
            return "Area Name not found";
        }
    }

    async function sendLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const area = await getAreaName(lat, lon);
                    
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        key: 'gps_info',
                        value: { lat: lat, lon: lon, area: area }
                    }, '*');
                },
                (err) => { console.warn(err.message); },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }
    }
    
    setInterval(sendLocation, 5000);
    sendLocation();
</script>
""", height=0)

# --- 3. UI ---
st.title("📍 Live Location & Area Tracker")
st.write("Checking your current Railway Section...")

# Session state se data lena
gps_info = st.session_state.get('gps_info')

if gps_info:
    # 1. Sabse pehle Area Name (Bade font mein)
    st.success("✅ Location Identified!")
    st.subheader(f"🏠 Area: {gps_info['area']}")
    
    st.divider()
    
    # 2. Coordinates (Chote font mein validation ke liye)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latitude", f"{gps_info['lat']:.6f}")
    with col2:
        st.metric("Longitude", f"{gps_info['lon']:.6f}")

    # 3. Quick Link
    maps_url = f"https://www.google.com/maps?q={gps_info['lat']},{gps_info['lon']}"
    st.info(f"📍 [Verify on Google Maps]({maps_url})")

else:
    st.warning("⏳ Waiting for GPS signal... Make sure Location is ON.")
    st.info("Tip: Agar 'Allow' popup aaye toh use click karein.")

st.divider()
st.caption("Phase 1.1: Area Name Validation | JE/TRD Mulchandani")
