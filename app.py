import io
import datetime
import requests
import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from PIL import Image, ImageDraw

# ReportLab Libraries for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 1. PAGE SETUP & CONFIGURATION ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

# Custom CSS for UI & Compact Buttons
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: #ffffff; }
    .main-title {
        color: #00E5FF;
        text-align: center;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .area-box { 
        padding: 15px; 
        background-color: #0d1b2a; 
        border-radius: 12px;
        border: 1px solid #1b263b;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1b263b;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #00E5FF;
    }
    /* Compact and Stylish Download Buttons */
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
        background-color: #00E5FF !important;
        color: #050a0f !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-size: 13px !important;
        min-height: 38px !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #00b4d8 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ OHE ATD Smart Tool</h1>", unsafe_allow_html=True)

# Helper Function: PDF Generator
def generate_pdf_bytes(data_dict, timestamp_str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#00E5FF'),
        spaceAfter=10,
        alignment=1
    )
    
    story.append(Paragraph("⚡ OHE ATD Calculation Record", title_style))
    story.append(Paragraph(f"<b>Generated On:</b> {timestamp_str}", ParagraphStyle('Sub', fontSize=10, alignment=1, textColor=colors.gray)))
    story.append(Spacer(1, 15))
    
    table_data = [["Parameter", "Value"]]
    for key, value in data_dict.items():
        table_data.append([key, str(value)])
        
    t = Table(table_data, colWidths=[220, 220])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b263b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1b263b')),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

# Helper Function: Pure Python PNG Generator (with Date/Time)
def generate_png_bytes(data_dict, timestamp_str):
    img = Image.new('RGB', (550, 420), color='#050a0f')
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rectangle([10, 10, 540, 410], outline='#00E5FF', width=2)
    
    # Title
    draw.text((160, 25), "⚡ OHE ATD CALCULATION RECORD", fill="#00E5FF")
    draw.line([25, 55, 525, 55], fill='#1b263b', width=1)
    
    # Parameters List
    y_pos = 75
    for key, val in data_dict.items():
        draw.text((35, y_pos), f"{key}:", fill="#8899a6")
        draw.text((260, y_pos), str(val), fill="#ffffff")
        draw.line([35, y_pos + 25, 515, y_pos + 25], fill='#0d1b2a', width=1)
        y_pos += 35
        
    # Timestamp Watermark Banner at Bottom
    draw.rectangle([10, 370, 540, 410], fill='#0d1b2a')
    draw.text((120, 385), f"Saved on: {timestamp_str}", fill="#00E5FF")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- 2. LOCATION & WEATHER FETCHING ---
st.markdown("### 📍 Location & Ambient Temperature Setup")

if "ambient_temp" not in st.session_state:
    st.session_state.ambient_temp = 35.0

col_geo, col_manual = st.columns([1, 1])

with col_geo:
    st.write("**Option A: Use GPS Location**")
    location = streamlit_geolocation()
    if location and location.get("latitude") and location.get("longitude"):
        try:
            lat = location["latitude"]
            lon = location["longitude"]
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(weather_url, timeout=5).json()
            if "current_weather" in response:
                current_temp = response["current_weather"]["temperature"]
                st.session_state.ambient_temp = float(current_temp)
                st.success(f"Live Temp: **{current_temp}°C**")
        except Exception:
            st.error("Failed to fetch live weather data.")

with col_manual:
    st.write("**Option B: Manual Input**")
    st.session_state.ambient_temp = st.number_input(
        "Set Temperature (°C)",
        min_value=-10.0,
        max_value=60.0,
        value=float(st.session_state.ambient_temp),
        step=0.5
    )

st.markdown("---")

# --- 3. ATD CALCULATION ENGINE ---
st.markdown("### 🔧 ATD Parameter Calculation")

with st.container():
    st.markdown("<div class='area-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        atd_type = st.selectbox("ATD Type", ["3:1 Pulley Type", "5:1 Winch Type", "Direct Rigid Type"])
        anchor_len = st.number_input("Tensioning Length L (m)", min_value=100, max_value=1500, value=750, step=50)
        
    with c2:
        conductor_type = st.selectbox("Conductor Type", ["Conventional (107 sq mm)", "High Speed (150 sq mm)"])
        std_temp = st.number_input("Standard/Mean Temp T0 (°C)", value=35, step=1)

    alpha = 0.000017  
    temp_diff = st.session_state.ambient_temp - std_temp
    movement = anchor_len * alpha * temp_diff * 1000  
    
    base_x = 950  
    base_y = 2500  
    
    calc_x = base_x + movement
    calc_y = base_y - movement

    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DISPLAY RESULTS ---
st.markdown("### 📊 Required Settings")

st.markdown(f"""
    <div id="record-card" class="area-box">
        <h3 style="color:#00E5FF; text-align:center; margin-top:0;">⚡ OHE ATD Calculation Summary</h3>
        <p style="text-align:center; color:#8899a6; font-size:0.9em;">
            Type: <b>{atd_type}</b> | Conductor: <b>{conductor_type}</b> | Length: <b>{anchor_len}m</b>
        </p>
        <hr style="border: 1px solid #1b263b;">
        <div style="display: flex; justify-content: space-around; gap: 10px; text-align: center;">
            <div class="metric-card" style="flex: 1;">
                <p style='margin:0; font-size: 0.85em; color:#8899a6;'>Ambient Temp</p>
                <h3 style="color:#00E5FF; margin: 5px 0 0 0;">{st.session_state.ambient_temp:.1f} °C</h3>
            </div>
            <div class="metric-card" style="flex: 1;">
                <p style='margin:0; font-size: 0.85em; color:#8899a6;'>'X' Value (Counterweight)</p>
                <h3 style="color:#00E5FF; margin: 5px 0 0 0;">{calc_x:.0f} mm</h3>
            </div>
            <div class="metric-card" style="flex: 1;">
                <p style='margin:0; font-size: 0.85em; color:#8899a6;'>'Y' Value (Pulleys Gap)</p>
                <h3 style="color:#00E5FF; margin: 5px 0 0 0;">{calc_y:.0f} mm</h3>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 5. SAVE RECORD OPTIONS ---
st.markdown("### 💾 Save Record")

record_data = {
    "ATD Type": atd_type,
    "Conductor Type": conductor_type,
    "Tensioning Length (L)": f"{anchor_len} m",
    "Standard Temp (T0)": f"{std_temp} °C",
    "Ambient Temp": f"{st.session_state.ambient_temp:.1f} °C",
    "Calculated X Value": f"{calc_x:.0f} mm",
    "Calculated Y Value": f"{calc_y:.0f} mm"
}

now_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

export_col1, export_col2 = st.columns(2)

with export_col1:
    pdf_buffer = generate_pdf_bytes(record_data, now_str)
    st.download_button(
        label="📄 Save PDF Record",
        data=pdf_buffer,
        file_name=f"ATD_Record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

with export_col2:
    png_buffer = generate_png_bytes(record_data, now_str)
    st.download_button(
        label="🖼️ Save PNG Image",
        data=png_buffer,
        file_name=f"ATD_Record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )
