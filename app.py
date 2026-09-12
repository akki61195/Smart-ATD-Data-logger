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
