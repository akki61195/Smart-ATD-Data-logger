import io
import streamlit as st
import pandas as pd
import requests
from streamlit_geolocation import streamlit_geolocation

# PDF Generation Imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 1. PAGE SETUP & CONFIGURATION ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp { 
        background-color: #050a0f; 
        color: #ffffff; 
    }
    .main-title {
        color: #00E5FF;
        text-align: center;
        font-weight: 700;
        margin-bottom: 20px;
    }
    #record-card {
        padding: 25px;
        background-color: #0d1b2a;
        border-radius: 12px;
        border: 1px solid #1b263b;
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
    .stButton>button {
        width: 100%;
        background-color: #00E5FF;
        color: #050a0f;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #00b4d8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Function: Generate PDF Byte Stream
def generate_pdf(data_dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#00E5FF'),
        spaceAfter=15,
        alignment=1
    )
    
    story.append(Paragraph("⚡ OHE ATD Calculation Record", title_style))
    story.append(Spacer(1, 15))
    
    table_data = [["Parameter", "Value"]]
    for key, value in data_dict.items():
        table_data.append([key, str(value)])
        
    t = Table(table_data, colWidths=[240, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b263b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1b263b')),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown("<h1 class='main-title'>⚡ OHE ATD Smart Tool</h1>", unsafe_allow_html=True)

# --- 2. LOCATION & WEATHER FETCHING ---
st.markdown("### 📍 Location & Ambient Temperature Setup")

if "ambient_temp" not in st.session_state:
    st.session_state.ambient_temp = 35.0

col_geo, col_manual = st.columns([1, 1])

with col_geo:
    st.write("**Option A: Use GPS Location**")
    location = streamlit_geolocation()
    
    if location and location.get("latitude") and location.get("longitude"):
        lat = location["latitude"]
        lon = location["longitude"]
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(weather_url, timeout=5).json()
            if "current_weather" in response:
                current_temp = response["current_weather"]["temperature"]
                st.session_state.ambient_temp = float(current_temp)
                st.success(f"Location found! Live Temp: **{current_temp}°C**")
        except Exception:
            st.error("Failed to fetch live weather data. Set manually.")

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

# --- 4. DISPLAY RESULTS & TARGET CAPTURE CARD ---
st.markdown("### 📊 Required Settings")

st.markdown(f"""
    <div id="record-card">
        <h3 style="color:#00E5FF; text-align:center; margin-top:0;">⚡ OHE ATD Calculation Summary</h3>
        <p style="text-align:center; color:#8899a6; font-size:0.9em;">
            Type: <b>{atd_type}</b> | Conductor: <b>{conductor_type}</b> | Length: <b>{anchor_len}m</b>
        </p>
        <hr style="border: 1px solid #1b263b;">
        <div style="display: flex; justify-content: space-around; gap: 10px; text-align: center;">
            <div class="metric-card" style="flex: 1;">
                <h4>Ambient Temp</h4>
                <h2 style="color:#00E5FF;">{st.session_state.ambient_temp:.1f} °C</h2>
            </div>
            <div class="metric-card" style="flex: 1;">
                <h4>'X' Value (Counterweight)</h4>
                <h2 style="color:#00E5FF;">{calc_x:.0f} mm</h2>
            </div>
            <div class="metric-card" style="flex: 1;">
                <h4>'Y' Value (Pulleys Gap)</h4>
                <h2 style="color:#00E5FF;">{calc_y:.0f} mm</h2>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SAVE & EXPORT OPTIONS ---
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

export_col1, export_col2 = st.columns(2)

with export_col1:
    # PDF Download Button
    pdf_buffer = generate_pdf(record_data)
    st.download_button(
        label="📄 Save Record as PDF",
        data=pdf_buffer,
        file_name=f"ATD_Record_{st.session_state.ambient_temp}C.pdf",
        mime="application/pdf"
    )

with export_col2:
    # Client-side Image Download using html2canvas
    st.components.v1.html("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
        function captureAndDownload() {
            var target = window.parent.document.getElementById("record-card");
            if (target) {
                html2canvas(target, { backgroundColor: '#050a0f' }).then(function(canvas) {
                    var link = document.createElement('a');
                    link.download = 'ATD_Record.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                });
            } else {
                alert("Target card not found!");
            }
        }
        </script>
        <button onclick="captureAndDownload()" style="
            width: 100%;
            background-color: #00E5FF;
            color: #050a0f;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            cursor: pointer;
            font-size: 14px;
            font-family: sans-serif;">
            📷 Save Record as Image (PNG)
        </button>
    """, height=45)
