import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64

# Custom CSS for fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400&family=Lexend:wght@600&display=swap');
    .title-font {
        font-family: 'Lexend', sans-serif;
        font-size: 36px;
    }
    .paragraph-font {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title with custom font
st.markdown('<p class="title-font">Conversión de Texto a Audio</p>', unsafe_allow_html=True)

# Display image
image = Image.open('Yoru - Taza.png')
st.image(image, width=350)

# Sidebar text
with st.sidebar:
    st.subheader("Escribe y/o selecciona texto para ser escuchado.")

# Create temp directory if not exists
if not os.path.exists("temp"):
    os.mkdir("temp")

# Subheader and paragraph with custom font
st.markdown('<p class="title-font">La corta historia de un pequeño fantasma</p>', unsafe_allow_html=True)
st.markdown('<p class="paragraph-font">¡Si que hace frío! De seguro que la leona está dormida, como no le gusta el frío.- exclamó el fantasma. '
            'Flotaba sobre la mesa del comedor, pensando en qué hacer. Antes de que se diera cuenta, sus dedos no se movían, eso muy posiblemente '
            'paso al ser congelados por el frío tan duro que atormentaba a todos. "... Bueno, ya ni modo." - tomó un tamaño pequeño, agarró unas '
            'esponjas cercanas y se acostó en una taza para dormir plácidamente hasta la mañana.</p>', unsafe_allow_html=True)

# Text input and language selection
st.markdown("¿Quieres escucharlo? Copia el texto a continuación:")
text = st.text_area("Ingrese el texto a escuchar.")
languages = {
    "Español": 'es',
    "Inglés": 'en',
    "Ruso": 'ru',
    "Japonés": 'ja',
    "Italiano": 'it'
}

option_lang = st.selectbox("Selecciona el lenguaje", list(languages.keys()))
lg = languages[option_lang]

# Text-to-speech function
def text_to_speech(text, lg):
    tts = gTTS(text, lang=lg)
    my_file_name = text[:20] if len(text) > 20 else "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, text

# Convert text to audio
if st.button("Convertir a Audio"):
    if text:
        result, output_text = text_to_speech(text, lg)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Download link for the audio file
        with open(f"temp/{result}.mp3", "rb") as f:
            data = f.read()
        def get_binary_file_downloader_html(bin_file, file_label='File'):
            bin_str = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
            return href
        st.markdown(get_binary_file_downloader_html(f"temp/{result}.mp3", file_label="Audio File"), unsafe_allow_html=True)

# Function to remove old files
def remove_files(n):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            os.remove(f)
