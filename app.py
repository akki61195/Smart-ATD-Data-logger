import streamlit as st
import pandas as pd
import requests # Nayi library live data ke liye

# --- PAGE CONFIG ---
st.set_page_config(page_title="ATD Smart Calc", page_icon="🌡️", layout="centered")

# --- LIVE TEMP FUNCTION ---
def get_live_temp(city="Surendranagar"):
    try:
        # OpenWeatherMap API (Free version)
        # Note: Professional use ke liye aap apni personal API key le sakte hain
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=da06f9774917a14e590230f30501f21a"
        response = requests.get(url).json()
        temp = response['main']['temp']
        return round(temp, 1)
    except:
        return 35.0 # Agar internet na ho toh default 35

# --- CSS (Wahi Dark Blue Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .auto-temp-box {
        background-color: rgba(0, 212, 255, 0.2);
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h2 style='text-align: center;'>OHE ATD Smart Calculator</h2>", unsafe_allow_html=True)

# --- AUTO TEMP FETCH ---
live_temp = get_live_temp("Surendranagar") # Aapka sheher

# --- INPUT SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    L = st.number_input("Tension Length (L)", value=750.0)

with col2:
    # Yahan temperature ab apne aap fetch hoga
    theta_2 = st.number_input("🌡️ Current Temp (°C)", value=live_temp, step=0.1)
    st.markdown(f"<div class='auto-temp-box'>Live: {live_temp}°C</div>", unsafe_allow_html=True)

# --- CALCULATIONS ---
alpha, theta_1 = 0.000017, 35
delta_1 = L * alpha * (theta_1 - theta_2) * 1000
x_val, y_val = 1300 + delta_1, 2300 + (3 * delta_1)

# --- RESULTS ---
st.write("#### Technical Output")
r1, r2 = st.columns(2)
r1.metric("X Value (Pulley)", f"{round(x_val, 1)} mm", f"{round(delta_1, 1)} mm")
r2.metric("Y Value (Weight)", f"{round(y_val, 1)} mm", f"{round(3*delta_1, 1)} mm")

st.markdown("<div style='position: fixed; bottom: 10px; width: 100%; text-align: center; font-size: 20px; opacity: 0.4;'>DEVELOPED BY: A.K.MULCHANDANI JE/TRD</div>", unsafe_allow_html=True)
