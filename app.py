import os
import streamlit as st
import base64
from PIL import Image
from gtts import gTTS
import openai
import io

# Función para convertir texto a audio
def text_to_speech(text):
    import uuid
    # Crear directorio "temp" si no existe
    if not os.path.exists("temp"):
        os.makedirs("temp")
    result = str(uuid.uuid4())
    output_path = f"temp/{result}.mp3"
    tts = gTTS(text, lang="es")
    tts.save(output_path)
    return result, output_path

# Configuración de Streamlit
st.set_page_config(page_title="Análisis de imagen", layout="centered", initial_sidebar_state="collapsed")
st.title("Lector de Manga")
st.sidebar.subheader("¡Obtén descripciones detalladas de tu manga!")

# Ingresar API Key
ke = st.text_input('Ingresa tu Clave API', type="password")
if ke:
    openai.api_key = ke

# Subir archivo de imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Ingresar detalles adicionales
show_details = st.checkbox("Adicionar detalles sobre la imagen", value=False)
if show_details:
    additional_details = st.text_area("Añade contexto adicional:")

# Botón para analizar la imagen
if st.button("Analizar la imagen"):
    if not ke:
        st.error("Por favor ingresa tu API Key.")
    elif not uploaded_file:
        st.error("Por favor sube una imagen.")
    else:
        with st.spinner("Analizando la imagen..."):
            try:
                # Leer la imagen y convertirla al formato RGB si es necesario
                image = Image.open(uploaded_file)
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Guardar la imagen en un buffer como JPEG
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # Crear el prompt de la solicitud
                prompt = (
                    "Eres un lector experto de manga. Describe en español lo que ves en la imagen de forma detallada. "
                    "Incluye los diálogos en un formato de guion y analiza cada panel como si fueras un narrador de manga. "
                    "El formato de guion será dando de ejemplo (Panel 1 , el personaje Juan ve a Pablo molesto y dice -mal-)."
                )
                if show_details and additional_details:
                    prompt += f"\n\nDetalles adicionales proporcionados: {additional_details}"

                # Solicitar la descripción a la API de OpenAI
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente experto en descripciones de imágenes y análisis de paneles de manga."},
                        {"role": "user", "content": prompt},
                        {"role": "user", "content": f"Imagen en base64: {img_str}"}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                description = response.choices[0].message['content']
                st.subheader("Descripción Generada:")
                st.markdown(description)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

# Sección para convertir texto a audio
text = st.text_area("Ingrese el texto a escuchar.")
if st.button("Convertir a Audio"):
    if text: 
        result, output_path = text_to_speech(text)
        audio_file = open(output_path, "rb")
        audio_bytes = audio_file.read()
        st.markdown("### Tu audio generado:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Opción para descargar el archivo de audio
        with open(output_path, "rb") as f:
            data = f.read()

        def get_binary_file_downloader_html(bin_file, file_label='Archivo'):
            bin_str = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Descargar {file_label}</a>'
            return href

        st.markdown(get_binary_file_downloader_html(output_path, file_label="Archivo de audio"), unsafe_allow_html=True)
    else:
        st.error("No hay texto disponible para convertir a audio. Por favor, analiza una imagen primero.")

