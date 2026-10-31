import io
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP & THEME TOGGLE ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

# Requirement 2: Light / Dark Mode Toggle (st.toggle, not radio)
dark_mode = st.toggle("🌙 Dark Mode", value=True)

if dark_mode:
    bg_color = "#050a0f"
    text_color = "#ffffff"
    card_bg = "#1c2128"
    border_accent = "#00d4ff"
    calc_val_color = "#ffb703"  # Requirement 3: Changed calculated value color
else:
    bg_color = "#f4f6f9"
    text_color = "#1e293b"
    card_bg = "#ffffff"
    border_accent = "#0077b6"
    calc_val_color = "#d97706"  # Requirement 3: Changed calculated value color (warm amber)

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .area-box {{ 
        padding: 15px; 
        background-color: {card_bg}; 
        border: 2px solid {border_accent}; 
        border-radius: 12px; 
        text-align: center;
        margin: 15px 0px;
    }}
    .area-label {{ color: {border_accent}; font-size: 14px; margin-bottom: 2px; font-weight: bold; }}
    .area-text {{ font-size: 18px; font-weight: bold; color: {text_color}; }}
    .length-display {{
        font-size: 24px !important;
        font-weight: bold;
        color: {calc_val_color};
        padding: 12px;
        background: {card_bg};
        border-radius: 8px;
        border-left: 8px solid {calc_val_color};
        margin: 10px 0px;
    }}
    .metric-calc-box {{
        background: {card_bg};
        border: 1px solid {border_accent};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
    }}
    .metric-calc-label {{
        font-size: 13px;
        font-weight: bold;
        color: {text_color};
        opacity: 0.8;
    }}
    .metric-calc-val {{
        font-size: 26px;
        font-weight: bold;
        color: {calc_val_color};
    }}
    .stButton>button {{
        background-color: {border_accent} !important;
        color: black !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. DATA LOADING ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"


@st.cache_data
def load_sheet_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except:
        return None


# --- 3. ADVANCED WEATHER ENGINE ---
def get_weather_by_coords(lat, lon):
    try:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, timeout=5).json()
        return round(float(w_res["current_weather"]["temperature"]), 1)
    except:
        return 35.0


def get_manual_city_data(city_name):
    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        res = requests.get(
            geo_url, headers={"User-Agent": "RailwayTool"}, timeout=5
        ).json()
        if res:
            lat, lon = res[0]["lat"], res[0]["lon"]
            temp = get_weather_by_coords(lat, lon)
            return temp, res[0]["display_name"]
        return 35.0, "City Not Found"
    except:
        return 35.0, "Network Error"


# --- 4. UI INITIALIZATION ---
st.markdown(
    f"<h2 style='text-align: center; color: {border_accent};'>OHE ATD Smart Tool</h2>",
    unsafe_allow_html=True,
)

if "temp_val" not in st.session_state:
    st.session_state.temp_val = 35.0
if "area_name" not in st.session_state:
    st.session_state.area_name = "GPS Not Active"

df = load_sheet_data()

# --- 5. STRUCTURE & LENGTH DISPLAY (Bigger Font) ---
if df is not None:
    struct_list = df["Structure_No"].dropna().unique().tolist()
    selected_struct = st.selectbox(
        "📍 Select Structure No", ["Manual Entry"] + struct_list
    )
    if selected_struct != "Manual Entry":
        L = float(
            df[df["Structure_No"] == selected_struct]["Tension_Length"].values[0]
        )
        st.markdown(
            f"<div class='length-display'>Tension Length (L): {L} m</div>",
            unsafe_allow_html=True,
        )
    else:
        L = st.number_input("Enter Tension Length (L) manually", value=750.0)
else:
    L = st.number_input("Enter Tension Length (L) manually", value=750.0)

st.divider()

# --- 6. LOCATION MODE ---
manual_loc = st.checkbox("✍️ Enter Location Manually")

if manual_loc:
    city_input = st.text_input(
        "Enter City Name (e.g. Kodinar, Junagadh)", value="Kodinar"
    )
    if st.button("🔍 FETCH TEMP FOR THIS CITY"):
        with st.spinner("Fetching data..."):
            t, a = get_manual_city_data(city_input)
            st.session_state.temp_val = t
            st.session_state.area_name = a
else:
    st.write("🛰️ GPS Mode")
    location = streamlit_geolocation()
    if location and location.get("latitude"):
        if st.button("🌡️ SYNC LIVE AREA & TEMP"):
            with st.spinner("Syncing..."):
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current_weather=true"
                w_res = requests.get(w_url, timeout=5).json()
                st.session_state.temp_val = round(
                    float(w_res["current_weather"]["temperature"]), 1
                )

                g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={location['latitude']}&lon={location['longitude']}"
                g_res = requests.get(
                    g_url, headers={"User-Agent": "RailwayTool"}, timeout=5
                ).json()
                st.session_state.area_name = g_res.get(
                    "display_name", "Local Section"
                )

# --- 7. DISPLAY & RESULTS ---
st.markdown(
    f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

theta_2 = st.number_input(
    "Current Temp (°C)", value=st.session_state.temp_val, step=0.1
)

# Calculation Logic (35°C Standard)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.divider()

# Requirement 1 & 3: Side-by-side calculated chart values and site measured inputs
col_x_calc, col_x_actual = st.columns(2)
with col_x_calc:
    st.markdown(
        f"""
        <div class="metric-calc-box">
            <div class="metric-calc-label">Calculated X (Chart Value)</div>
            <div class="metric-calc-val">{round(x_val, 1)} mm</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_x_actual:
    x_measured = st.number_input(
        "Site Measured X (mm)", value=float(round(x_val, 1)), step=1.0
    )

col_y_calc, col_y_actual = st.columns(2)
with col_y_calc:
    st.markdown(
        f"""
        <div class="metric-calc-box">
            <div class="metric-calc-label">Calculated Y (Chart Value)</div>
            <div class="metric-calc-val">{round(y_val, 1)} mm</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_y_actual:
    y_measured = st.number_input(
        "Site Measured Y (mm)", value=float(round(y_val, 1)), step=1.0
    )

# --- 8. IMAGE CARD GENERATOR ---
ist_offset = timezone(timedelta(hours=5, minutes=30))
curr_dt = datetime.now(ist_offset).strftime("%d-%b-%Y %I:%M:%S %p")

struct_disp = selected_struct if "selected_struct" in locals() else "N/A"
area_disp = st.session_state.get("area_name", "Manual Mode")

scale = 3
width, height = 900 * scale, 570 * scale
img = Image.new("RGB", (width, height), color="#050a0f")
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.load_default(size=25 * scale)
    font_body = ImageFont.load_default(size=17 * scale)
    font_val = ImageFont.load_default(size=19 * scale)
except Exception:
    font_title = font_body = font_val = ImageFont.load_default()

# Outer Border & Title Header
draw.rectangle(
    [20 * scale, 20 * scale, width - 20 * scale, height - 20 * scale],
    outline="#00d4ff",
    width=5 * scale,
)
draw.text(
    (40 * scale, 40 * scale),
    "⚡ OHE ATD SMART TOOL RECORD",
    fill="#00d4ff",
    font=font_title,
)
draw.line(
    [(40 * scale, 100 * scale), (width - 40 * scale, 100 * scale)],
    fill="#00d4ff",
    width=3 * scale,
)

# Text Content Lines with Location and Structure Info
lines = [
    f"📅 Date & Time: {curr_dt}",
    f"📍 Location / Section: {area_disp[:40]}",
    f"🏗️ Structure No: {struct_disp}",
    f"📏 Tension Length (L): {L} m",
    f"🌡️ Temperature: {theta_2} °C",
]

y_off = 120 * scale
for line in lines:
    draw.text((40 * scale, y_off), line, fill="#ffffff", font=font_body)
    y_off += 40 * scale

# Output Box showing both Chart Value & Site Measured Value
draw.rectangle(
    [40 * scale, 340 * scale, width - 40 * scale, 520 * scale],
    fill="#1c2128",
    outline="#00d4ff",
    width=3 * scale,
)
draw.text(
    (60 * scale, 360 * scale),
    f"X (Chart): {x_val:.0f} mm  |  X (Measured): {x_measured:.0f} mm",
    fill="#ffb703",
    font=font_val,
)
draw.text(
    (60 * scale, 430 * scale),
    f"Y (Chart): {y_val:.0f} mm  |  Y (Measured): {y_measured:.0f} mm",
    fill="#ffb703",
    font=font_val,
)

# PNG Buffer Export
buf = io.BytesIO()
img.save(buf, format="PNG")

# --- 9. DOWNLOAD BUTTON & TOAST ---
st.markdown(
    """<style>
    div[data-testid="stDownloadButton"] {
        display: flex;
        justify-content: center;
        margin-top: 15px;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #002b49 !important;
        color: #ccff00 !important;
        border: 2px solid #00d4ff !important;
        font-weight: bold !important;
        font-size: 18px !important;
        width: 240px !important;
        height: 50px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #004070 !important;
        color: #ffffff !important;
    }
    </style>""",
    unsafe_allow_html=True,
)


def notify_save():
    st.toast("✅ Image Saved Successfully!", icon="💾")


st.download_button(
    label="💾 SAVE IMG",
    data=buf.getvalue(),
    file_name=f"ATD_Record_{datetime.now(ist_offset).strftime('%Y%m%d_%H%M%S')}.png",
    mime="image/png",
    on_click=notify_save,
)
st.markdown(
    f"<div style='text-align: center; font-size: 10px; margin-top: 40px; opacity: 0.6;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>",
    unsafe_allow_html=True,
)
