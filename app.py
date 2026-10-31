# --- 7. DISPLAY & RESULTS (WITH ANIMATED THERMOMETER) ---
st.markdown(
    f"""
    <div class="area-box">
        <div class="area-label">📡 ACTIVE SECTION</div>
        <div class="area-text">{st.session_state.area_name}</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 1. Manual adjustment ya direct fetched value select karne ke liye input
col_therm, col_input = st.columns([1.2, 1])

with col_input:
    st.markdown("#### 🌡️ Temperature Setting")
    theta_2 = st.number_input(
        "Current Ambient Temp (°C)",
        value=float(st.session_state.temp_val),
        step=0.5,
        min_value=-5.0,
        max_value=60.0,
        help="GPS/City se auto-fetch hua hai. Agar site pe calibrated thermometer ka reading alag hai to manually edit kar sakte hain.",
    )
    # Quick indicator text
    if theta_2 >= 40:
        temp_status = (
            "<span style='color: #ff3366;'>🔥 High Ambient (Summer)</span>"
        )
    elif theta_2 <= 15:
        temp_status = (
            "<span style='color: #00d4ff;'>❄️ Low Ambient (Winter)</span>"
        )
    else:
        temp_status = (
            "<span style='color: #00ff41;'>⚡ Normal Range (35° Std Base)</span>"
        )

    st.markdown(
        f"<div style='font-size: 13px; margin-top: -5px;'>Condition: {temp_status}</div>",
        unsafe_allow_html=True,
    )

# 2. Percentage calculation for Mercury column height (Range: 0°C to 55°C)
min_scale = 0.0
max_scale = 55.0
clamped_temp = max(min_scale, min(theta_2, max_scale))
mercury_percent = int(((clamped_temp - min_scale) / (max_scale - min_scale)) * 100)

# Color dynamics: Neela (cold) -> Green (optimum) -> Lal (hot)
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
    # Responsive CSS-animated Realistic Thermometer
    thermometer_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 10px; background: {card_bg}; border-radius: 12px; border: 1px solid {border_accent};">
        <style>
            @keyframes riseMercury {{
                0% {{ height: 5%; }}
                100% {{ height: {mercury_percent}%; }}
            }}
            .thermo-tube {{
                position: relative;
                width: 22px;
                height: 140px;
                background: #0f141c;
                border: 2px solid #3a4759;
                border-bottom: none;
                border-radius: 14px 14px 0 0;
                overflow: hidden;
                display: flex;
                align-items: flex-end;
                margin: 0 auto;
            }}
            .thermo-mercury {{
                width: 100%;
                height: {mercury_percent}%;
                background: linear-gradient(to top, {mercury_color}, #ffdd00);
                border-radius: 10px 10px 0 0;
                box-shadow: 0 0 12px {glow_color};
                animation: riseMercury 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            }}
            .thermo-bulb {{
                width: 42px;
                height: 42px;
                background: {mercury_color};
                border: 2px solid #3a4759;
                border-radius: 50%;
                margin: -6px auto 0 auto;
                box-shadow: 0 0 15px {glow_color};
            }}
            .temp-readout {{
                font-size: 26px;
                font-weight: 800;
                color: {mercury_color};
                text-shadow: 0 0 8px {glow_color};
                text-align: center;
                margin-top: 6px;
            }}
        </style>
        
        <div style="text-align: center; margin-right: 15px;">
            <div class="thermo-tube">
                <div class="thermo-mercury"></div>
            </div>
            <div class="thermo-bulb"></div>
        </div>

        <div>
            <div style="font-size: 11px; color: #8c9ba5; letter-spacing: 1px; font-weight: bold;">LIVE AMBIENT</div>
            <div class="temp-readout">{theta_2:.1f}°C</div>
            <div style="font-size: 11px; color: {text_color}; opacity: 0.7;">Ref: 35.0°C base</div>
        </div>
    </div>
    """
    st.components.v1.html(thermometer_html, height=210)

# Calculation Logic (35°C Standard)
delta = L * 0.000017 * (35 - theta_2) * 1000
x_val, y_val = 1300 + delta, 2300 + (3 * delta)
