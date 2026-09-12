import io
import streamlit as st
import pandas as pd
import requests
from streamlit_geolocation import streamlit_geolocation

# PDF Library
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="OHE ATD Smart Tool", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: white; }
    .area-box { 
        padding: 15px; 
        background-color: #0d1b2a; 
        border-radius: 10px;
        border: 1px solid #1b263b;
        margin-bottom: 15px;
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
    </style>
""", unsafe_allow_html=True)

st.title("⚡ OHE ATD Smart Tool")

# PDF Generation Helper
def generate_pdf(data_dict):
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
        spaceAfter=15,
        alignment=1
    )
    
    story.append(Paragraph("OHE ATD Calculation Record", title_style))
    story.append(Spacer(1, 10))
    
    table_data = [["Parameter", "Value"]]
    for key, value in data_dict.items():
        table_data.append([key, str(value)])
        
    t = Table(table_data, colWidths=[230, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b263b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0d1b2a')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1b263b')),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- 2. LOCATION & WEATHER SETUP ---
if "ambient_temp" not in st.session_state:
    st.session_state.ambient_temp = 35.0

col_geo, col_manual = st.columns([1, 1])

with col_geo:
    st.write("**Option A: GPS Location**")
    location = streamlit_geolocation()
    if location and location.get("latitude") and location.get("longitude"):
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&current_weather=true"
            res = requests.get(weather_url, timeout=5).json()
            if "current_weather" in res:
                st.session_state.ambient_temp = float(res["current_weather"]["temperature"])
                st.success(f"Temp: **{st.session_state.ambient_temp}°C**")
        except:
            st.error("Error fetching weather.")

with col_manual:
    st.write("**Option B: Manual Input**")
    st.session_state.ambient_temp = st.number_input("Temp (°C)", value=float(st.session_state.ambient_temp), step=0.5)

st.markdown("---")

# --- 3. ATD CALCULATION ---
st.markdown("<div class='area-box'>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    atd_type = st.selectbox("ATD Type", ["3:1 Pulley Type", "5:1 Winch Type", "Direct Rigid Type"])
    anchor_len = st.number_input("Tensioning Length L (m)", min_value=100, max_value=1500, value=750, step=50)
with c2:
    conductor_type = st.selectbox("Conductor Type", ["Conventional (107 sq mm)", "High Speed (150 sq mm)"])
    std_temp = st.number_input("Standard Temp T0 (°C)", value=35, step=1)

alpha = 0.000017
temp_diff = st.session_state.ambient_temp - std_temp
movement = anchor_len * alpha * temp_diff * 1000

calc_x = 950 + movement
calc_y = 2500 - movement
st.markdown("</div>", unsafe_allow_html=True)

# --- 4. RESULTS DISPLAY ---
# Wrapped with id="record-card" for Image Capture
st.markdown(f"""
    <div id="record-card" style="padding: 10px; background-color: #050a0f;">
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div class='metric-card' style='flex:1;'>
                <p style='margin:0; font-size: 0.9em;'>Ambient Temp</p>
                <h3 style='margin:5px 0 0 0; color:#00E5FF;'>{st.session_state.ambient_temp:.1f} °C</h3>
            </div>
            <div class='metric-card' style='flex:1;'>
                <p style='margin:0; font-size: 0.9em;'>'X' Value</p>
                <h3 style='margin:5px 0 0 0; color:#00E5FF;'>{calc_x:.0f} mm</h3>
            </div>
            <div class='metric-card' style='flex:1;'>
                <p style='margin:0; font-size: 0.9em;'>'Y' Value</p>
                <h3 style='margin:5px 0 0 0; color:#00E5FF;'>{calc_y:.0f} mm</h3>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SAVE RECORD OPTIONS ---
record_data = {
    "ATD Type": atd_type,
    "Conductor Type": conductor_type,
    "Tensioning Length (L)": f"{anchor_len} m",
    "Standard Temp (T0)": f"{std_temp} °C",
    "Ambient Temp": f"{st.session_state.ambient_temp:.1f} °C",
    "Calculated X Value": f"{calc_x:.0f} mm",
    "Calculated Y Value": f"{calc_y:.0f} mm"
}

col_pdf, col_img = st.columns(2)

with col_pdf:
    pdf_file = generate_pdf(record_data)
    st.download_button(
        label="📄 Save Record as PDF",
        data=pdf_file,
        file_name=f"ATD_Record_{st.session_state.ambient_temp}C.pdf",
        mime="application/pdf"
    )

with col_img:
    st.components.v1.html("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
        function captureCard() {
            var el = window.parent.document.getElementById("record-card");
            if (el) {
                html2canvas(el, { backgroundColor: '#050a0f' }).then(function(canvas) {
                    var a = document.createElement('a');
                    a.download = 'ATD_Record.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                });
            }
        }
        </script>
        <button onclick="captureCard()" style="
            width: 100%;
            background-color: #00E5FF;
            color: #050a0f;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px;
            cursor: pointer;
            font-size: 14px;
            font-family: sans-serif;">
            📷 Save Record as Image (PNG)
        </button>
    """, height=45)
