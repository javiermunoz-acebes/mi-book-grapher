import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# Instrucciones para que la IA actúe como un experto en Nano Banana Pro
model = genai.GenerativeModel(
    model_name="models/gemini-2.0-flash-lite",
    system_instruction="Eres un experto en diseño de infografías literarias. Tu meta es crear prompts para 'Nano Banana Pro' que incluyan texto legible y diagramas claros."
)
# Si el anterior falla, usa el nombre completo del catálogo:
# model_name="gemini-1.5-flash"
# Función técnica para leer archivos PDF
def leer_pdf(file):
    reader = PyPDF2.PdfReader(file)
    texto_completo = ""
    for page in reader.pages[:5]: # Leemos las primeras 5 páginas para rapidez
        texto_completo += page.extract_text()
    return texto_completo

# --- 2. DISEÑO VISUAL (ESTILO AZUL) ---
st.set_page_config(page_title="Generador de Prompts Infográficos", layout="centered")

st.markdown("""
    <style>
    .header-blue {
        background-color: #3b4cca;
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .stButton>button { border-radius: 20px; }
    </style>
    <div class="header-blue">
        <h1 style='margin:0; color:white;'>🖊️ Generador de Prompts Infográficos</h1>
        <p style='margin:0; opacity:0.8;'>Crea prompts perfectos para Nano Banana Pro.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. FORMULARIO DE ENTRADA ---
idioma = st.selectbox("Idioma del Texto en la Infografía", ["Español", "Inglés", "Francés"])

tema = st.text_input("Tema Principal (Libro)", placeholder="Ej: Introducción a la Filología Digital")

col1, col2 = st.columns(2)
with col1:
    audiencia = st.text_input("Audiencia Objetivo", placeholder="Ej: Estudiantes Universitarios")
with col2:
    titulo_infog = st.text_input("Título de la Infografía", placeholder="Ej: Del texto al byte")

# Sección de Importar Contenido
st.write("### Contenido / Datos Clave")
archivo = st.file_uploader("Importar Contenido (PDF)", type=["pdf"])

resumen_puntos = ""
if archivo:
    with st.spinner("Leyendo libro..."):
        texto_pdf = leer_pdf(archivo)
        # Gemini extrae los puntos clave automáticamente
        prompt_resumen = f"Extrae los 5 puntos más importantes de este texto para una infografía: {texto_pdf}"
        resumen_puntos = model.generate_content(prompt_resumen).text
        st.success("✅ Contenido importado con éxito")

contenido = st.text_area("Descripción de los hechos o pasos", value=resumen_puntos, height=150)

# --- 4. ESTILO Y RECOMENDACIÓN ---
if st.button("Recomendar Estilo y Diseño"):
    with st.spinner("Analizando..."):
        sugerencia = model.generate_content(f"Sugiere estilo y diseño para una infografía sobre: {tema}")
        st.info(sugerencia.text)

col3, col4 = st.columns(2)
with col3:
    estilo = st.selectbox("Estilo Visual", ["Minimalista", "Ilustración 3D", "Vintage", "Moderno"])
with col4:
    diseno = st.selectbox("Diseño / Distribución", ["Cronológico", "Diagrama de flujo", "Comparativo"])

formato = st.radio("Formato / Relación de Aspecto", ["Cuadrado", "Vertical", "Horizontal"], horizontal=True)

# --- 5. GENERACIÓN FINAL ---
if st.button("🚀 Generar Prompt Maestro", type="primary", use_container_width=True):
    with st.spinner("Creando prompt técnico..."):
        prompt_final = f"""
        Crea un prompt para Nano Banana Pro. 
        Tema: {tema}. Idioma: {idioma}. Título: {titulo_infog}.
        Audiencia: {audiencia}. Estilo: {estilo}. Diseño: {diseno}.
        Puntos clave: {contenido}. Formato: {formato}.
        Instrucción: El texto debe ser nítido y legible en {idioma}.
        """
        resultado = model.generate_content(prompt_final)
        st.subheader("Tu Prompt para Nano Banana Pro:")
        st.code(resultado.text)
        st.balloons()
genai.configure(api_key=API_KEY)

# --- BLOQUE DE DIAGNÓSTICO ---
# Esto nos dirá en los logs qué modelos puede ver tu clave realmente
print("Buscando modelos disponibles...")
disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
print(f"Modelos que tu cuenta puede ver: {disponibles}")

# Intentamos usar el primero de la lista si el flash falla
try:
    nombre_modelo = "gemini-1.5-flash"
    model = genai.GenerativeModel(model_name=nombre_modelo)
    print(f"Modelo {nombre_modelo} configurado exitosamente.")
except Exception as e:
    print(f"Error configurando {nombre_modelo}: {e}")
# ------------------------------
