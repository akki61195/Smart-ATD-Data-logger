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
   .length-display {
       font-size: 24px !important;
       font-weight: bold;
       color: #00ff41;
       padding: 12px;
       background: #1c2128;
       border-radius: 8px;
       border-left: 8px solid #00ff41;
       margin: 10px 0px;
   }
   .stButton>button {
       background-color: #00d4ff !important;
       color: black !important;
       font-weight: bold !important;
       width: 100% !important;
       height: 3.5em !important;
       border-radius: 10px;
   }
   </style>
   """, unsafe_allow_html=True)

# --- 2. DATA LOADING ---
SHEET_ID = "1vfioGSmpC7a5S8SMUpCk9xn-mtttvcTecLEQ1Sd6XkU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_sheet_data():
try:
df = pd.read_csv(SHEET_URL)
df.columns = df.columns.str.strip()
return df
except: return None

# --- 3. ADVANCED WEATHER ENGINE ---
def get_weather_by_coords(lat, lon):
try:
w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
w_res = requests.get(w_url, timeout=5).json()
return round(float(w_res['current_weather']['temperature']), 1)
except: return 35.0

def get_manual_city_data(city_name):
try:
# City name se Lat/Lon nikalna
geo_url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
res = requests.get(geo_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
if res:
lat, lon = res[0]['lat'], res[0]['lon']
temp = get_weather_by_coords(lat, lon)
return temp, res[0]['display_name']
return 35.0, "City Not Found"
except: return 35.0, "Network Error"

# --- 4. UI INITIALIZATION ---
st.markdown("<h2 style='text-align: center; color: #00d4ff;'>OHE ATD Smart Tool</h2>", unsafe_allow_html=True)

if 'temp_val' not in st.session_state: st.session_state.temp_val = 35.0
if 'area_name' not in st.session_state: st.session_state.area_name = "GPS Not Active"

df = load_sheet_data()

# --- 5. STRUCTURE & LENGTH DISPLAY (Bigger Font) ---
if df is not None:
struct_list = df['Structure_No'].dropna().unique().tolist()
selected_struct = st.selectbox("📍 Select Structure No", ["Manual Entry"] + struct_list)
if selected_struct != "Manual Entry":
L = float(df[df['Structure_No'] == selected_struct]['Tension_Length'].values[0])
st.markdown(f"<div class='length-display'>Tension Length (L): {L} m</div>", unsafe_allow_html=True)
else: L = st.number_input("Enter Tension Length (L) manually", value=750.0)
else: L = st.number_input("Enter Tension Length (L) manually", value=750.0)

st.divider()

# --- 6. LOCATION MODE ---
manual_loc = st.checkbox("✍️ Enter Location Manually")

if manual_loc:
city_input = st.text_input("Enter City Name (e.g. Kodinar, Junagadh)", value="Kodinar")
if st.button("🔍 FETCH TEMP FOR THIS CITY"):
with st.spinner('Fetching data...'):
t, a = get_manual_city_data(city_input)
st.session_state.temp_val = t
st.session_state.area_name = a
else:
st.write("🛰️ GPS Mode")
location = streamlit_geolocation()
if location and location.get('latitude'):
if st.button("🌡️ SYNC LIVE AREA & TEMP"):
with st.spinner('Syncing...'):
w_url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current_weather=true"
w_res = requests.get(w_url, timeout=5).json()
st.session_state.temp_val = round(float(w_res['current_weather']['temperature']), 1)

g_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={location['latitude']}&lon={location['longitude']}"
g_res = requests.get(g_url, headers={'User-Agent': 'RailwayTool'}, timeout=5).json()
st.session_state.area_name = g_res.get('display_name', 'Local Section')

# --- 7. DISPLAY & RESULTS ---
st.markdown(f"""
   <div class="area-box">
       <div class="area-label">📡 ACTIVE SECTION</div>
       <div class="area-text">{st.session_state.area_name}</div>
   </div>
""", unsafe_allow_html=True)

theta_2 = st.number_input("Current Temp (°C)", value=st.session_state.temp_val, step=0.1)

# Calculation Logic (35°C Standard)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)

st.divider()
c1, c2 = st.columns(2)
c1.metric("X (Pulley Gap)", f"{round(x_val, 1)} mm")
c2.metric("Y (Weight Height)", f"{round(y_val, 1)} mm")

st.markdown(f"<div style='text-align: center; font-size: 10px; margin-top: 40px; opacity: 0.6;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)

import io
import datetime
from PIL import Image, ImageDraw, ImageFont

# PDF Generation Libraries
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- CSS FOR SMALL ELEGANT BUTTONS ---
st.markdown("""
    <style>
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        height: auto !important;
        min-height: 38px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SAVE RECORD SECTION ---
st.markdown("---")
st.markdown("##### 💾 Save Calculation Record")

# Safely fetch current parameter values
t_val = st.session_state.ambient_temp if "ambient_temp" in st.session_state else 34.10
x_val = calc_x if 'calc_x' in locals() else 1306.7
y_val = calc_y if 'calc_y' in locals() else 2320.0
now_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# 1. PDF GENERATOR FUNCTION
def generate_pdf_bytes(t, x, y, timestamp_str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0d1b2a'),
        spaceAfter=10,
        alignment=1
    )
    
    story.append(Paragraph("⚡ OHE ATD CALCULATION RECORD", title_style))
    story.append(Paragraph(f"<b>Generated On:</b> {timestamp_str}", ParagraphStyle('Sub', fontSize=10, alignment=1, textColor=colors.gray)))
    story.append(Spacer(1, 15))
    
    table_data = [
        ["Parameter", "Calculated Value"],
        ["Ambient Temperature", f"{t:.2f} °C"],
        ["X Value (Pulley Gap)", f"{x:.1f} mm"],
        ["Y Value (Weight Height)", f"{y:.1f} mm"]
    ]
    
    t_table = Table(table_data, colWidths=[200, 200])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b263b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ]))
    
    story.append(t_table)
    doc.build(story)
    buffer.seek(0)
    return buffer

# 2. PNG IMAGE GENERATOR FUNCTION
def generate_png_bytes(t, x, y, timestamp_str):
    img = Image.new('RGB', (550, 360), color='#050a0f')
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rectangle([10, 10, 540, 350], outline='#00E5FF', width=2)
    
    # Header
    draw.text((160, 25), "⚡ OHE ATD RECORD", fill="#00E5FF")
    draw.line([25, 55, 525, 55], fill='#1b263b', width=1)
    
    # Time Stamp
    draw.text((30, 70), f"Date & Time: {timestamp_str}", fill="#8899a6")
    
    # Cards
    draw.rectangle([30, 105, 520, 165], fill='#0d1b2a', outline='#1b263b')
    draw.text((45, 125), f"Ambient Temp: {t:.2f} °C", fill="#ffffff")
    
    draw.rectangle([30, 180, 520, 245], fill='#1b263b', outline='#00E5FF')
    draw.text((45, 195), "X (Pulley Gap):", fill="#8899a6")
    draw.text((45, 215), f"{x:.1f} mm", fill="#00E5FF")
    
    draw.rectangle([30, 260, 520, 325], fill='#1b263b', outline='#00E5FF')
    draw.text((45, 275), "Y (Weight Height):", fill="#8899a6")
    draw.text((45, 295), f"{y:.1f} mm", fill="#00E5FF")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- BUTTONS LAYOUT ---
col_pdf, col_img = st.columns(2)

with col_pdf:
    pdf_bytes = generate_pdf_bytes(t_val, x_val, y_val, now_str)
    st.download_button(
        label="📄 Save PDF",
        data=pdf_bytes,
        file_name=f"ATD_Record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

with col_img:
    png_bytes = generate_png_bytes(t_val, x_val, y_val, now_str)
    st.download_button(
        label="🖼️ Save PNG Image",
        data=png_bytes,
        file_name=f"ATD_Record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )
