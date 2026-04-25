import streamlit as st
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. CSS (Railway Field Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f !important; color: #ffffff !important; }
    label p { color: #00d4ff !important; font-weight: bold !important; }
    div[data-testid="stMetricValue"] > div { color: #00ff41 !important; font-weight: 800; font-size: 36px !important; }
    .stButton>button { background-color: #00d4ff !important; color: black !important; font-weight: bold !important; width: 100% !important; height: 3.8em !important; border-radius: 12px !important; }
    .footer-credit { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 11px; background-color: #050a0f; color: #ffffff; border-top: 1px solid #30363d; z-index: 100; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GEOLOCATION JAVASCRIPT ---
# Ye script browser se lat/lon nikal kar Streamlit ke widgets mein bhej degi
st.components.v1.html("""
<script>
    const options = { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 };
    function getLocation() {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
                window.parent.postMessage({
                    type: 'streamlit:set_widget_value',
                    key: 'gps_data',
                    value: coords
                }, '*');
            },
            (err) => { console.warn("GPS Error: " + err.message); },
            options
        );
    }
    // Auto-trigger on load
    getLocation();
</script>
""", height=0)

# --- 4. WEATHER FUNCTION ---
def get_weather(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(w_url, timeout=5).json()
        temp = round(float(res['current_weather']['temperature']), 1)
        
        # Area Name
        g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        g_res = requests.get(g_url, headers={'User-Agent': 'RailwayATD'}, timeout=5).json()
        area = g_res.get('address', {}).get('city') or g_res.get('address', {}).get('town') or g_res.get('address', {}).get('village') or "Field Site"
        return temp, area
    except:
        return 35.0, "Manual Set"

# --- 5. UI ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "Waiting for GPS..."

L = st.number_input("Tension Length (L) in meters", value=750.0, step=1.0)

# --- 6. SYNC ACTION ---
if st.button("🛰️ SYNC WITH MOBILE GPS"):
    gps = st.session_state.get('gps_data')
    if gps:
        with st.spinner('Fetching local weather...'):
            t, a = get_weather(gps['lat'], gps['lon'])
            st.session_state.temp_val = t
            st.session_state.area_name = a
            st.rerun()
    else:
        st.warning("GPS Signal lock nahi hua. Browser settings check karein aur refresh karein.")

theta_2 = st.number_input("🌡️ Working Temp (°C)", value=st.session_state.temp_val, step=0.1)
st.caption(f"📍 Location: {st.session_state.area_name}")

# --- 7. CALCULATIONS ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.markdown("---")
r1, r2 = st.columns(2)
r1.metric("X (Pulley)", f"{round(x_val, 1)} mm")
r2.metric("Y (Weight)", f"{round(y_val, 1)} mm")

st.markdown("<div class='footer-credit'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
