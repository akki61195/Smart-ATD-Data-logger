import datetime

# --- SAVE RECORD BUTTONS ---
st.markdown("### 💾 Save Record")

# Safely capture calculated values or fall back to default
x_val = calc_x if 'calc_x' in locals() else 1300.0
y_val = calc_y if 'calc_y' in locals() else 2300.0

export_df = pd.DataFrame([{
    "X Value (Pulley Gap)": x_val,
    "Y Value (Weight Height)": y_val,
    "Date & Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}])

col_csv, col_img = st.columns(2)

with col_csv:
    st.download_button(
        label="📄 Save Record as CSV",
        data=export_df.to_csv(index=False),
        file_name=f"ATD_Record_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col_img:
    st.components.v1.html("""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
        function captureWithTimestamp() {
            var el = window.parent.document.querySelector('.stApp') || window.parent.document.body;
            
            var now = new Date();
            var timeString = "Saved on: " + now.toLocaleDateString() + " at " + now.toLocaleTimeString();

            var watermark = window.parent.document.createElement('div');
            watermark.id = "temp-timestamp-watermark";
            watermark.innerText = timeString;
            watermark.style.cssText = 'text-align: center; color: #00E5FF; padding: 10px; font-weight: bold; font-family: sans-serif; background: #050a0f; border-top: 1px solid #1b263b;';
            
            el.appendChild(watermark);

            html2canvas(el, { backgroundColor: '#050a0f' }).then(function(canvas) {
                var a = document.createElement('a');
                a.download = 'ATD_Record_' + now.toISOString().slice(0,10) + '.png';
                a.href = canvas.toDataURL('image/png');
                a.click();
                
                watermark.remove();
            });
        }
        </script>
        <button onclick="captureWithTimestamp()" style="
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
