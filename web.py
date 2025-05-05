import streamlit as st
import requests
import time
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
import google.generativeai as genai
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pandas as pd
from gtts import gTTS
import os
import base64

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

# Konfigurasi OpenWeatherMap
OPENWEATHER_API_KEY = "005228598cb7cced1e24ff9fdfc5fc72"  # Ganti dengan API key Anda
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Inisialisasi session state untuk history
if 'history' not in st.session_state:
    st.session_state.history = []

# UI
st.title("🧢 SmartCap Monitoring dengan Deskripsi AI (Gemini)")
st.divider()

status_placeholder = st.empty()
metric_placeholder = st.empty()
description_placeholder = st.empty()
audio_placeholder = st.empty()  # Placeholder untuk audio

# Fungsi untuk mendapatkan kondisi cahaya
def get_light_condition(lux):
    if lux > 1000:
        return "Terang"
    elif 100 <= lux <= 1000:
        return "Redup"
    else:
        return "Gelap"

# Ambil data cuaca
def get_weather():
    try:
        params = {
            'q': 'Malang',  # Ganti dengan kota Anda
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'id'
        }
        response = requests.get(WEATHER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            weather_condition = data['weather'][0]['description']
            
            # Kategorikan kondisi cuaca
            if 'cerah' in weather_condition.lower():
                return "Cerah"
            elif 'hujan' in weather_condition.lower():
                return "Hujan"
            else:
                return "Mendung"
        return "Tidak diketahui"
    except:
        return "Tidak diketahui"

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

# Fungsi untuk membuat audio dari teks
def text_to_speech(text, lang='id'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("output.mp3")
        
        # Baca file audio dan encode ke base64
        with open("output.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Buat HTML audio player
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Browser Anda tidak mendukung elemen audio.
            </audio>
        """
        
        return audio_html
    except Exception as e:
        return f"Error generating audio: {str(e)}"
    finally:
        # Hapus file audio setelah digunakan
        if os.path.exists("output.mp3"):
            os.remove("output.mp3")

# Deskripsi AI
def describe_environment_gemini(light_level):
    if light_level is not None:
        weather_condition = get_weather()
        prompt = f"Deskripsikan suasana dan kemungkinan kondisi cuaca berdasarkan intensitas cahaya {light_level:.2f} lux dan kondisi cuaca {weather_condition}."
        try:
            response = gemini_model.generate_content(prompt)
            return response.text, weather_condition
        except Exception as e:
            return f"Terjadi kesalahan saat menghubungi Gemini: {e}", "Tidak diketahui"
    else:
        return "Data cahaya belum tersedia untuk dideskripsikan.", "Tidak diketahui"

# Tombol ambil data manual
if st.button("💡 Ambil dan Deskripsikan Suasana"):
    lux = get_data()
    if lux is not None:
        metric_placeholder.metric("Cahaya (Lux)", f"{lux:.2f} Lux")
        description, weather_condition = describe_environment_gemini(lux)
        description_placeholder.markdown(f"Deskripsi AI (Gemini): {description}")
        
        # Generate audio dari deskripsi
        audio_html = text_to_speech(description)
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        
        # Tambahkan ke history
        light_condition = get_light_condition(lux)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({
            'Tanggal': timestamp,
            'Cahaya': light_condition,
            'Cuaca': weather_condition,
            'Deskripsi': description
        })

# Auto-refresh
auto_refresh_describe = st.checkbox("Auto-refresh dan Deskripsikan setiap 5 detik")

if auto_refresh_describe:
    # Autorefresh setiap 5 detik
    st_autorefresh(interval=5000, key="data_refresh")

    lux = get_data()
    if lux is not None:
        metric_placeholder.metric("Cahaya (Lux)", f"{lux:.2f} Lux")
        description, weather_condition = describe_environment_gemini(lux)
        description_placeholder.markdown(f"Deskripsi AI (Gemini): {description}")
        
        # Generate audio dari deskripsi
        audio_html = text_to_speech(description)
        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
        
        # Tambahkan ke history
        light_condition = get_light_condition(lux)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({
            'Tanggal': timestamp,
            'Cahaya': light_condition,
            'Cuaca': weather_condition,
            'Deskripsi': description
        })

# Tampilkan history
st.divider()
st.subheader("📜 History Monitoring")

if st.session_state.history:
    # Konversi ke DataFrame untuk tampilan yang lebih rapi
    history_df = pd.DataFrame(st.session_state.history)
    
    # Urutkan berdasarkan tanggal terbaru
    history_df = history_df.sort_values('Tanggal', ascending=False)
    
    # Tampilkan tabel
    st.table(history_df)
    
    # Tombol untuk clear history
    if st.button("🧹 Clear History"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("Belum ada data history. Klik tombol 'Ambil dan Deskripsikan Suasana' untuk mulai mencatat.")