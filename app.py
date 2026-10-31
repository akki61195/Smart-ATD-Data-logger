import base64
from datetime import datetime, timedelta, timezone
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import requests
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

# --- 2. THEME & HEADER TOGGLE ---
if "dark_mode" not in st.session_state:
  st.session_state.dark_mode = True

top_col1, top_col2 = st.columns([3, 1])
with top_col1:
  st.markdown("### ⚡ OHE ATD Smart Tool")
with top_col2:
  is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
  if is_dark != st.session_state.dark_mode:
    st.session_state.dark_mode = is_dark
    st.rerun()

if st.session_state.dark_mode:
  bg_color = "#050a0f"
  text_color = "#ffffff"
  card_bg = "#161b22"
  border_accent = "#00d4ff"
  calc_val_color = "#ffb703"
else:
  bg_color = "#f4f6f9"
  text_color = "#1e293b"
  card_bg = "#ffffff"
  border_accent = "#0077b6"
  calc_val_color = "#d97706"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    
    .area-box {{ 
        padding: 10px 14px; 
        background-color: {card_bg}; 
        border: 1.5px solid {border_accent}; 
        border-radius: 10px; 
        text-align: center;
        margin: 8px 0px;
    }}
    .area-label {{ color: {border_accent}; font-size: 12px; font-weight: bold; }}
    .area-text {{ font-size: 15px; font-weight: 600; color: {text_color}; }}

    .length-display {{
        font-size: 20px !important;
        font-weight: bold;
        color: {calc_val_color};
        padding: 8px 14px;
        background: {card_bg};
        border-radius: 8px;
        border-left: 6px solid {calc_val_color};
        margin: 6px 0px;
        text-align: center;
    }}

    .metric-calc-box {{
        background: {card_bg};
        border: 1.5px solid {border_accent};
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }}
    .metric-calc-label {{
        font-size: 13px;
        font-weight: bold;
        color: {text_color};
        opacity: 0.85;
    }}
    .metric-calc-val {{
        font-size: 26px;
        font-weight: bold;
        color: {calc_val_color};
        margin-top: 2px;
    }}

    .stButton>button {{
        background-color: {border_accent} !important;
        color: black !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 2.8em !important;
        border-radius: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. DATA LOADING ---
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


# --- 4. WEATHER ENGINE ---
def fetch_weather(lat, lon):
  try:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}¤t=temperature_2m¤t_weather=true"
    res = requests.get(url, timeout=6).json()
    if "current" in res and "temperature_2m" in res["current"]:
      return round(float(res["current"]["temperature_2m"]), 1)
    elif "current_weather" in res and "temperature" in res["current_weather"]:
      return round(float(res["current_weather"]["temperature"]), 1)
    return 35.0
  except Exception:
    return 35.0


def fetch_city_weather(city_name):
  try:
    geo_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(city_name)}&format=json&limit=1"
    res = requests.get(
        geo_url, headers={"User-Agent": "OHE_Railway_ATD_Tool"}, timeout=6
    ).json()
    if res and len(res) > 0:
      lat = float(res[0]["lat"])
      lon = float(res[0]["lon"])
      temp = fetch_weather(lat, lon)
      return temp, res[0].get("display_name", city_name)
    return 35.0, "City Not Found"
  except Exception:
    return 35.0, "Network Error"


# --- 5. INITIAL STATE ---
if "current_temp" not in st.session_state:
  st.session_state.current_temp = 35.0
if "temp_sync_ver" not in st.session_state:
  st.session_state.temp_sync_ver = 0
if "area_name" not in st.session_state:
  st.session_state.area_name = "GPS Not Active"

df = load_sheet_data()

# --- 6. STRUCTURE SELECTION ---
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

# --- 7. LOCATION MODE ---
manual_loc = st.checkbox("✍️ Enter Location Manually", value=False)

if manual_loc:
  c1, c2 = st.columns([2.5, 1.2])
  with c1:
    city_input = st.text_input(
        "Enter City Name", value="Kodinar", label_visibility="collapsed"
    )
  with c2:
    if st.button("🔍 FETCH"):
      with st.spinner("Fetching..."):
        t, a = fetch_city_weather(city_input)
        st.session_state.current_temp = float(t)
        st.session_state.temp_sync_ver += 1
        st.session_state.area_name = a
        st.rerun()
else:
  c1, c2 = st.columns([1.5, 2])
  with c1:
    location = streamlit_geolocation()
  with c2:
    if st.button("🌡️ SYNC LIVE AREA & TEMP"):
      if location and location.get("latitude") and location.get("longitude"):
        with st.spinner("Syncing..."):
          lat = location["latitude"]
          lon = location["longitude"]
          live_temp = fetch_weather(lat, lon)
          st.session_state.current_temp = float(live_temp)
          st.session_state.temp_sync_ver += 1

          try:
            g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
            g_res = requests.get(
                g_url, headers={"User-Agent": "OHE_Railway_ATD_Tool"}, timeout=6
            ).json()
            st.session_state.area_name = g_res.get(
                "display_name", f"Lat: {lat:.3f}, Lon: {lon:.3f}"
            )
          except Exception:
            st.session_state.area_name = f"Lat: {lat:.3f}, Lon: {lon:.3f}"
          st.rerun()
      else:
        st.toast("⚠️ Pehle ⌖ icon dabayein, phir Sync karein!", icon="📍")

# Active Section Banner
st.markdown(
    f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 8. TEMPERATURE & ANIMATED THERMOMETER (BALANCED SIDE-BY-SIDE) ---
col_therm, col_temp = st.columns([1, 1.6])

with col_temp:
  theta_2 = st.number_input(
      "Current Temp (°C)",
      value=float(st.session_state.current_temp),
      step=0.5,
      min_value=-5.0,
      max_value=60.0,
      key=f"temp_val_{st.session_state.temp_sync_ver}",
  )
  st.session_state.current_temp = float(theta_2)

  if theta_2 >= 40:
    temp_status = (
        "<span style='color: #ff3366; font-weight: bold;'>🔥 High Ambient"
        " (Summer)</span>"
    )
  elif theta_2 <= 15:
    temp_status = (
        "<span style='color: #00d4ff; font-weight: bold;'>❄️ Low Ambient"
        " (Winter)</span>"
    )
  else:
    temp_status = (
        "<span style='color: #00ff41; font-weight: bold;'>⚡ Standard Range"
        " (35° Base)</span>"
    )

  st.markdown(
      f"<div style='font-size: 13px; margin-top: 4px;'>Status:"
      f" {temp_status}</div>",
      unsafe_allow_html=True,
  )

min_scale, max_scale = 0.0, 55.0
clamped_temp = max(min_scale, min(theta_2, max_scale))
mercury_percent = int(
    ((clamped_temp - min_scale) / (max_scale - min_scale)) * 100
)

if theta_2 < 20:
  mercury_color = "#00d4ff"
  glow_color = "rgba(0, 212, 255, 0.6)"
elif theta_2 < 38:
  mercury_color = "#00ff41"
  glow_color = "rgba(0, 255, 65, 0.6)"
else:
  mercury_color = "#ff3366"
  glow_color = "rgba(255, 51, 102, 0.6)"

with col_therm:
  thermometer_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 12px; height: 110px; background: {card_bg}; border-radius: 10px; border: 1.5px solid {border_accent}; padding: 6px;">
        <style>
            @keyframes riseMercury {{
                0% {{ height: 5%; }}
                100% {{ height: {mercury_percent}%; }}
            }}
            .thermo-tube {{
                position: relative;
                width: 14px;
                height: 65px;
                background: #0f141c;
                border: 1.5px solid #3a4759;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                overflow: hidden;
                display: flex;
                align-items: flex-end;
                margin: 0 auto;
            }}
            .thermo-mercury {{
                width: 100%;
                height: {mercury_percent}%;
                background: linear-gradient(to top, {mercury_color}, #ffdd00);
                border-radius: 6px 6px 0 0;
                box-shadow: 0 0 8px {glow_color};
                animation: riseMercury 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            }}
            .thermo-bulb {{
                width: 26px;
                height: 26px;
                background: {mercury_color};
                border: 1.5px solid #3a4759;
                border-radius: 50%;
                margin: -4px auto 0 auto;
                box-shadow: 0 0 10px {glow_color};
            }}
            .temp-readout {{
                font-size: 22px;
                font-weight: 800;
                color: {mercury_color};
                text-shadow: 0 0 6px {glow_color};
                line-height: 1.1;
            }}
        </style>
        
        <div style="text-align: center;">
            <div class="thermo-tube">
                <div class="thermo-mercury"></div>
            </div>
            <div class="thermo-bulb"></div>
        </div>

        <div>
            <div style="font-size: 11px; color: #8c9ba5; font-weight: bold; letter-spacing: 0.5px;">AMBIENT</div>
            <div class="temp-readout">{theta_2:.1f}°C</div>
        </div>
    </div>
    """
  st.components.v1.html(thermometer_html, height=125)

# --- 9. CALCULATION & VALUES (GRID) ---
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.divider()

col_x1, col_x2 = st.columns(2)
with col_x1:
  st.markdown(
      f"""<div class="metric-calc-box">
        <div class="metric-calc-label">Calculated X (Chart)</div>
        <div class="metric-calc-val">{round(x_val, 1)} mm</div>
    </div>""",
      unsafe_allow_html=True,
  )
with col_x2:
  x_measured = st.number_input(
      "Site Measured X (mm)", value=float(round(x_val, 1)), step=1.0
  )

col_y1, col_y2 = st.columns(2)
with col_y1:
  st.markdown(
      f"""<div class="metric-calc-box">
        <div class="metric-calc-label">Calculated Y (Chart)</div>
        <div class="metric-calc-val">{round(y_val, 1)} mm</div>
    </div>""",
      unsafe_allow_html=True,
  )
with col_y2:
  y_measured = st.number_input(
      "Site Measured Y (mm)", value=float(round(y_val, 1)), step=1.0
  )

# --- 10. ULTRA HD IMAGE CARD GENERATOR ---
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

buf = io.BytesIO()
img.save(buf, format="PNG")

# --- 11. SAVE & SHARE BUTTONS ---
b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
file_name_ts = (
    f"ATD_Record_{datetime.now(ist_offset).strftime('%Y%m%d_%H%M%S')}.png"
)

share_text = f"""⚡ *OHE ATD INSPECTION RECORD* ⚡
📅 Date: {curr_dt}
📍 Section: {area_disp[:35]}
🏗️ Mast: {struct_disp}
📏 Tension Length (L): {L} m
🌡️ Temp: {theta_2} °C
-----------------------------
🔹 *X (Pulley Gap):* Calc {x_val:.0f} mm | Measured {x_measured:.0f} mm
🔹 *Y (Weight Ht):* Calc {y_val:.0f} mm | Measured {y_measured:.0f} mm
-----------------------------
_Report generated via OHE ATD Smart Tool_"""

encoded_text = urllib.parse.quote(share_text)
whatsapp_fallback_url = f"https://api.whatsapp.com/send?text={encoded_text}"

btn_col1, btn_col2 = st.columns(2)
with btn_col1:

  def notify_save():
    st.toast("✅ Image Saved Successfully!", icon="💾")

  st.download_button(
      label="💾 SAVE IMAGE",
      data=buf.getvalue(),
      file_name=file_name_ts,
      mime="image/png",
      on_click=notify_save,
      use_container_width=True,
  )

with btn_col2:
  share_button_html = f"""
    <div style="display: flex; justify-content: center;">
        <button id="shareBtn" style="
            background-color: #25D366;
            color: white;
            border: 1.5px solid #20ba5a;
            font-weight: bold;
            font-size: 14px;
            width: 100%;
            height: 42px;
            border-radius: 8px;
            cursor: pointer;
        ">📲 SHARE REPORT</button>
    </div>

    <script>
    document.getElementById('shareBtn').onclick = async function() {{
        const b64Data = '{b64_img}';
        const fileName = '{file_name_ts}';
        const shareMsg = decodeURIComponent('{encoded_text}');

        try {{
            const byteCharacters = atob(b64Data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], {{ type: 'image/png' }});
            const file = new File([blob], fileName, {{ type: 'image/png' }});

            if (navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                await navigator.share({{
                    title: 'OHE ATD Record',
                    text: shareMsg,
                    files: [file]
                }});
            }} else if (navigator.share) {{
                await navigator.share({{
                    title: 'OHE ATD Record',
                    text: shareMsg
                }});
            }} else {{
                window.open('{whatsapp_fallback_url}', '_blank');
            }}
        }} catch (err) {{
            window.open('{whatsapp_fallback_url}', '_blank');
        }}
    }};
    </script>
    """
  st.components.v1.html(share_button_html, height=52)

st.markdown(
    "<div style='text-align: center; font-size: 10px; margin-top: 25px;"
    " opacity: 0.6;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>",
    unsafe_allow_html=True,
)
