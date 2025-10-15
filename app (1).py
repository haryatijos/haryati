import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI STREAMLIT DAN API KEY
# ==============================================================================

# Ambil API Key dari Streamlit Secrets
# PASTI: Pastikan Anda memiliki file .streamlit/secrets.toml
# dengan kunci: GEMINI_API_KEY = "AIzaSy..."
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🚨 Kesalahan Konfigurasi: 'GEMINI_API_KEY' tidak ditemukan di Streamlit Secrets.")
    st.info("Buat file `.streamlit/secrets.toml` dan tambahkan `GEMINI_API_KEY = 'KUNCI_ANDA'`")
    st.stop()


# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
# --- CONTOH : CHATBOT AHLI EKONOMI ---
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli ekonomi. beri 2 kejadian tentang inflasi dan APBN"]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan contoh data inflasi dan APBN."]
    }
]

# ==============================================================================
# FUNGSI INISIALISASI DAN CORE LOGIC
# ==============================================================================

# Konfigurasi dan inisialisasi Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4, 
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi Gemini: {e}")
    st.stop()


# Judul Aplikasi
st.title("💰 Chatbot Ahli Ekonomi Gemini")
st.caption(f"Didukung oleh Google Gemini ({MODEL_NAME})")


# Inisialisasi Riwayat Obrolan (Session State)
# Streamlit mempertahankan riwayat di st.session_state.messages
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT
    st.session_state.chat = model.start_chat(history=INITIAL_CHATBOT_CONTEXT)
elif "chat" not in st.session_state:
    # Ini menangani kasus di mana pesan ada tetapi objek chat hilang (misal: restart)
    st.session_state.chat = model.start_chat(history=st.session_state.messages)


# Tampilkan riwayat obrolan
for message in st.session_state.messages:
    # Gunakan 'user' untuk peran 'user' dan 'assistant' untuk peran 'model'
    with st.chat_message(message["role"] if message["role"] == "user" else "assistant"):
        st.markdown(message["parts"][0])


# Input Pengguna
if prompt := st.chat_input("Tanyakan tentang Inflasi atau APBN..."):
    # 1. Tampilkan input pengguna di antarmuka
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Tambahkan input ke riwayat session state
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # 3. Kirim pesan ke Gemini dan tampilkan respons
    with st.chat_message("assistant"):
        with st.spinner("Gemini sedang berpikir..."):
            try:
                # Kirim pesan menggunakan objek chat yang sudah ada di session state
                response = st.session_state.chat.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
                
                # 4. Tambahkan respons ke riwayat session state
                st.session_state.messages.append({"role": "model", "parts": [full_response]})

            except Exception as e:
                error_message = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "model", "parts": [error_message]})
