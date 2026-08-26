import streamlit as st
import cv2
import tempfile
import os
from apng import APNG
from PIL import Image

# 1. Configuración de la ventana y el diseño
st.set_page_config(
    page_title="APNG Studio & Converter",
    page_icon="🎬",
    layout="centered"
)

# Estilos CSS personalizados para una interfaz oscura, limpia y profesional
st.markdown("""
<style>
    /* Estilos generales */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Botones personalizados */
    .stButton>button {
        width: 100%;
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
    }

    /* Tarjeta informativa */
    .info-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        margin-top: 25px;
    }
    .info-card h4 {
        margin-top: 0;
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.title("🎬 APNG Studio & Converter")
st.caption("Herramienta de conversión de secuencias PNG y videos MP4 a formato APNG.")

st.divider()

# 2. Selector de origen de datos y parámetros
col1, col2 = st.columns([1, 1])

with col1:
    modo = st.radio("Origen de datos:", ("Secuencia de imágenes (PNG)", "Video (MP4)"))

with col2:
    fps = st.slider("Velocidad de reproducción (FPS):", min_value=1, max_value=60, value=15)

archivos = None

if modo == "Secuencia de imágenes (PNG)":
    archivos = st.file_uploader("Selecciona o arrastra imágenes PNG", type=["png"], accept_multiple_files=True)
else:
    archivos = st.file_uploader("Selecciona o arrastra un archivo MP4", type=["mp4"])

# 3. Lógica de procesamiento
if archivos:
    if st.button("Generar APNG"):
        barra_progreso = st.progress(0)
        texto_estado = st.empty()
        
        temp_dir = tempfile.mkdtemp()
        frames_paths = []

        # Procesar lista de PNGs
        if modo == "Secuencia de imágenes (PNG)":
            texto_estado.text("Procesando fotogramas PNG...")
            for i, archivo in enumerate(archivos):
                ruta_temp = os.path.join(temp_dir, f"frame_{i:04d}.png")
                with open(ruta_temp, "wb") as f:
                    f.write(archivo.getbuffer())
                frames_paths.append(ruta_temp)
                barra_progreso.progress(int(((i + 1) / len(archivos)) * 50))

        # Procesar video MP4
        else:
            texto_estado.text("Extrayendo fotogramas del video MP4...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                tmp_video.write(archivos.read())
                video_path = tmp_video.name

            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            count = 0

            while True:
                ret, frame = cap.read()
                if not ret: 
                    break
                frame_path = os.path.join(temp_dir, f"frame_{count:04d}.png")
                cv2.imwrite(frame_path, frame)
                frames_paths.append(frame_path)
                count += 1
                if total_frames > 0:
                    barra_progreso.progress(min(int((count / total_frames) * 50), 50))
            cap.release()

        # Compilar animación APNG
        texto_estado.text("Ensamblando el archivo APNG final...")
        animacion = APNG()
        delay = int(1000 / fps)
        
        for i, path in enumerate(frames_paths):
            animacion.append_file(path, delay=delay, delay_den=1000)
            barra_progreso.progress(50 + int(((i + 1) / len(frames_paths)) * 50))

        ruta_salida = os.path.join(temp_dir, "animacion.png")
        animacion.save(ruta_salida)
        
        texto_estado.text("¡Proceso completado con éxito!")
        barra_progreso.progress(100)

        # Descarga del archivo
        with open(ruta_salida, "rb") as file:
            st.download_button(
                label="📥 Descargar APNG Resultante",
                data=file,
                file_name="animacion_optimizada.png",
                mime="image/png"
            )

# 4. Sección Informativa Profesional
st.markdown("""
<div class="info-card">
    <h4>💡 Sobre el formato APNG (Animated Portable Network Graphics)</h4>
    <p><b>APNG</b> es una extensión del formato de imagen PNG que permite animaciones manteniendo una calidad superior a la de los GIFs tradicionales.</p>
    <ul>
        <li><b>Calidad de color:</b> Compatible con profundidad de color de 24 bits y canal alfa de transparencia de 8 bits.</li>
        <li><b>Compatibilidad:</b> Soporte nativo en todos los navegadores modernos (Chrome, Firefox, Edge, Safari, Opera) y aplicaciones como Discord y Telegram.</li>
        <li><b>Retrocompatibilidad:</b> En sistemas no compatibles, se visualiza automáticamente el primer fotograma como una imagen PNG estática.</li>
    </ul>
</div>
""", unsafe_allow_html=True)