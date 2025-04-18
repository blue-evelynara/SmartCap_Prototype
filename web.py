import streamlit as st
import requests
import time
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
import google.generativeai as genai
from streamlit_autorefresh import st_autorefresh

# Konfigurasi API
GEMINI_API_KEY = "AIzaSyDF-lLuhIG9Hm0FvPMU0RhxmgKDqQpuadA"
genai.configure(api_key=GEMINI_API_KEY)

# Inisialisasi model Gemini
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# Token & Endpoint Ubidots
TOKEN = "BBUS-eCkv24LYNvWw8SKQR0TWg1z3SlCWuC"
DEVICE_LABEL = "corelogic"
VARIABLE_LABEL = "cahaya"
URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_LABEL}/lv"
headers = {"X-Auth-Token": TOKEN}

# UI
st.title("🧢 SmartCap Monitoring dengan Deskripsi AI (Gemini)")
st.divider()

status_placeholder = st.empty()
metric_placeholder = st.empty()
description_placeholder = st.empty()

# Ambil data dari Ubidots
def get_data():
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            lux = float(response.text)
            status_placeholder.success("✅ Data berhasil diambil.")
            return lux
        else:
            status_placeholder.error(f"❌ Gagal ambil data: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        status_placeholder.error(f"❌ Gagal mengambil data: {e}")
        return None

# Deskripsi AI
def describe_environment_gemini(light_level):
    if light_level is not None:
        prompt = f"Deskripsikan suasana dan kemungkinan kondisi cuaca berdasarkan intensitas cahaya {light_level:.2f} lux."
        try:
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Terjadi kesalahan saat menghubungi Gemini: {e}"
    else:
        return "Data cahaya belum tersedia untuk dideskripsikan."

# Tombol ambil data manual
if st.button("💡 Ambil dan Deskripsikan Suasana"):
    lux = get_data()
    if lux is not None:
        metric_placeholder.metric("Cahaya (Lux)", f"{lux:.2f} Lux")
        description = describe_environment_gemini(lux)
        description_placeholder.markdown(f"*Deskripsi AI (Gemini):* {description}")

# Auto-refresh
auto_refresh_describe = st.checkbox("Auto-refresh dan Deskripsikan setiap 5 detik")

if auto_refresh_describe:
    # Autorefresh setiap 5 detik
    st_autorefresh(interval=5000, key="data_refresh")

    lux = get_data()
    if lux is not None:
        metric_placeholder.metric("Cahaya (Lux)", f"{lux:.2f} Lux")
        description = describe_environment_gemini(lux)
        description_placeholder.markdown(f"*Deskripsi AI (Gemini):* {description}")
