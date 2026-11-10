import logging
import os
import random
import re
import time
from html.parser import HTMLParser
from io import BytesIO
from xml.sax.saxutils import escape

# Librería de IA faltante que provocaba el error "Groq is not defined"
from groq import Groq

# Conversor de HTML a PDF con manejo seguro de excepciones
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

# Componentes de Streamlit y control de persistencia local
import streamlit as st
from streamlit_cookies_controller import CookieController

# Módulos propios del proyecto
from lector_pdf import extraer_texto_pdf
from ia_motor import adaptar_cv_con_ia


# ---------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Adaptador de CV Solidario",
    page_icon="💼",
    layout="wide",
)

MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB
COOKIE_USOS = "cv_usos_gratuitos"
TIEMPO_CAPTCHA = 30


# ---------------------------------------------------------------------
# Validación y transformación de contenido
# ---------------------------------------------------------------------
def validar_firma_pdf(archivo) -> bool:
    """Comprueba la firma PDF y restaura la posición del archivo."""
    try:
        posicion = archivo.tell()
        archivo.seek(0)
        firma = archivo.read(5)
        archivo.seek(posicion)
        return firma == b"%PDF-"
    except Exception:
        return False


class _TextoDesdeHTML(HTMLParser):
    """Extrae texto de HTML sin conservar etiquetas ni atributos."""

    BLOQUES = {
        "p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3",
        "h4", "section", "article", "tr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.BLOQUES:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in self.BLOQUES:
            self.partes.append("\n")

    def handle_data(self, data):
        self.partes.append(data)

    def texto(self):
        texto = "".join(self.partes)
        texto = texto.replace("\xa0", " ")
        texto = re.sub(r"[ \t]+\n", "\n", texto)
        texto = re.sub(r"\n[ \t]+", "\n", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        return texto.strip()


def limpiar_todo_para_ats(texto_html):
    """Limpia profundamente HTML, Markdown, enlaces y unifica los saltos de línea."""
    if not texto_html:
        return ""
    
    # 1. Eliminar etiquetas HTML completas y residuos
    texto = re.compile(r'<[^>]+>').sub('', texto_html)
    texto = re.compile(r'</?[a-zA-Z]*\s*$').sub('', texto)
    
    # 2. Eliminar marcadores Markdown
    texto = texto.replace('**', '').replace('__', '')
    texto = re.compile(r'^#+\s+', re.MULTILINE).sub('', texto)
    texto = re.compile(r'\[([^\]]+)\]\([^\)]+\)').sub(r'\1', texto)
    
    # 3. Cortar comentarios finales intrusivos de la IA
    patrones_corte = [
        r"(?i)\bEste CV ha sido adaptado\b",
        r"(?i)\bNota:\b",
        r"(?i)\bAlineación con\b",
        r"(?i)\bEspero que este currículum\b"
    ]
    for patron in patrones_corte:
        partes = re.split(patron, texto, maxsplit=1)
        if len(partes) > 1:
            texto = partes[0]
            
    # 4. TRUCO DE INGENIERÍA: Unificar múltiples Enters continuos en saltos simples
    # Esto evita que al pegar en Word se interprete como párrafos gigantes espaciados
    texto = re.compile(r'\n\s*\n+').sub('\n\n', texto)
    
    return texto.strip()

def obtener_api_key_servidor():
    """Lee la clave desde Streamlit Secrets o variables de entorno."""
    try:
        clave = st.secrets.get("GROQ_API_KEY")
        if clave:
            return str(clave).strip()
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "").strip()


def leer_usos_cookie(cookies) -> int:
    """Lee la cookie sin permitir que un valor inválido rompa la aplicación."""
    try:
        valor = cookies.get(COOKIE_USOS)
        usos = int(valor) if valor is not None else 0
        return max(0, usos)
    except (TypeError, ValueError, Exception):
        return 0


# ---------------------------------------------------------------------
# Estado de sesión y CAPTCHA
# ---------------------------------------------------------------------
if "verificado_humano" not in st.session_state:
    st.session_state.verificado_humano = False

if "cv_html" not in st.session_state:
    st.session_state.cv_html = None

if "captcha_num1" not in st.session_state:
    st.session_state.captcha_num1 = random.randint(1, 9)
    st.session_state.captcha_num2 = random.randint(1, 9)
    st.session_state.captcha_resultado = (
        st.session_state.captcha_num1 + st.session_state.captcha_num2
    )
    st.session_state.captcha_inicio_tiempo = time.time()

cookies = CookieController()
usos_guardados = leer_usos_cookie(cookies)
api_key_servidor = obtener_api_key_servidor()


# ---------------------------------------------------------------------
# Escenario A: verificación antibots
# ---------------------------------------------------------------------
if not st.session_state.verificado_humano:
    transcurrido = time.time() - st.session_state.captcha_inicio_tiempo
    restante = max(0, int(TIEMPO_CAPTCHA - transcurrido))

    if restante <= 0:
        st.session_state.captcha_num1 = random.randint(1, 9)
        st.session_state.captcha_num2 = random.randint(1, 9)
        st.session_state.captcha_resultado = (
            st.session_state.captcha_num1 + st.session_state.captcha_num2
        )
        st.session_state.captcha_inicio_tiempo = time.time()
        st.rerun()

    _, col_box, _ = st.columns(3)
    with col_box:
        st.markdown(
            "<div style='text-align:center'><h2>🛡️ Verificación de Seguridad</h2>"
            "<p>Confirma que eres una persona para acceder a la herramienta.</p></div>",
            unsafe_allow_html=True,
        )
        st.divider()

        pregunta = (
            f"¿Cuánto es {st.session_state.captcha_num1} + "
            f"{st.session_state.captcha_num2}?"
        )
        respuesta = st.number_input(
            pregunta, step=1, value=0, key="unico_input_captcha"
        )
        st.write(f"⏳ El reto expira en aproximadamente: **{restante} segundos**")
        st.progress(restante / TIEMPO_CAPTCHA)

        if st.button("🔓 Verificar y Entrar", type="primary", use_container_width=True):
            transcurrido = time.time() - st.session_state.captcha_inicio_tiempo
            if transcurrido < 1:
                st.error("🛑 Resuelve la operación con calma.")
            elif respuesta != st.session_state.captcha_resultado:
                st.error("🛑 El resultado es incorrecto. Inténtalo de nuevo.")
            else:
                st.session_state.verificado_humano = True
                st.rerun()

    st.stop()


# ---------------------------------------------------------------------
# Escenario B: aplicación principal
# ---------------------------------------------------------------------
st.title("💼 Adaptador de CV con IA (100% Gratuito)", anchor=False)
st.subheader(
    "Optimiza tu currículum para la oferta de empleo que deseas",
    anchor=False,
)
st.write(
    "Esta herramienta analiza los requisitos de la empresa y adapta "
    "estratégicamente tu perfil. Las mejoras se incorporan al contenido "
    "del currículum para alinearlo con la oferta de empleo."
)
st.divider()


# ---------------------------------------------------------------------
# Barra lateral: API, privacidad y tutorial
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("🔑 Configuración y Llave de IA", anchor=False)

    if usos_guardados < 1:
        st.success("✨ Tienes 1 uso de prueba gratuito activado.")
        api_key_usuario = st.text_input(
            "🔑 API Key de Groq (opcional para el primer uso):",
            type="password",
        )
        api_key_a_usar = api_key_usuario.strip() or api_key_servidor
    else:
        st.warning(
            "⏳ Ya has utilizado la prueba gratuita en este navegador. "
            "Introduce tu propia API Key para continuar:"
        )
        api_key_usuario = st.text_input(
            "🔑 Introduce tu API Key de Groq:", type="password"
        )
        api_key_a_usar = api_key_usuario.strip()

    with st.expander("💡 Guía rápida: consigue tu API Key"):
        st.markdown(
            "1. Entra en [Groq Cloud Console](https://console.groq.com/).\n"
            "2. Inicia sesión.\n"
            "3. Abre **API Keys** y crea una clave.\n"
            "4. Copia la clave y pégala en el campo anterior."
        )

    with st.expander("🔒 Tu privacidad"):
        st.markdown(
            "- No necesitas identificarte para usar la herramienta.\n"
            "- El CV se procesa para generar la adaptación solicitada.\n"
            "- La cookie técnica se utiliza para contabilizar el uso gratuito "
            "en este navegador."
        )


# ---------------------------------------------------------------------
# Formulario y procesamiento
# ---------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("1. Tus Datos", anchor=False)
    archivo_subido = st.file_uploader(
        "Sube tu CV actual en formato PDF", type=["pdf"]
    )
    texto_oferta = st.text_area(
        "Pega la descripción de la oferta de empleo:",
        height=350,
        placeholder="Ej.: Buscamos un desarrollador Python con experiencia...",
    )

with col2:
    st.header("2. CV Adaptado", anchor=False)
    boton_adaptar = st.button(
        "✨ Adaptar Currículum Ahora", type="primary"
    )

    if boton_adaptar:
        if not api_key_a_usar:
            st.error("⚠️ Introduce una API Key de Groq en la barra lateral.")
        elif archivo_subido is None:
            st.error("⚠️ Por favor, sube tu currículum en PDF.")
        elif not texto_oferta.strip():
            st.error("⚠️ Por favor, pega la oferta de empleo.")
        elif archivo_subido.size > MAX_PDF_BYTES:
            st.error("⚠️ El PDF supera el límite permitido de 10 MB.")
        elif not validar_firma_pdf(archivo_subido):
            st.error("⚠️ El archivo no tiene una firma PDF válida.")
        else:
            fase = "extracción del texto del PDF"

            try:
                with st.spinner(
                    "Analizando la oferta y adaptando tu CV..."
                ):
                    archivo_subido.seek(0)
                    texto_cv = extraer_texto_pdf(archivo_subido)

                    if not texto_cv:
                        raise ValueError(
                            "El extractor no ha devuelto texto."
                        )

                    if not isinstance(texto_cv, str):
                        raise TypeError(
                            f"El extractor ha devuelto un tipo inesperado: "
                            f"{type(texto_cv).__name__}"
                        )

                    if texto_cv.startswith("Error al leer"):
                        raise ValueError(texto_cv)

                    fase = "comunicación con la API de Groq"

                    cv_generado = adaptar_cv_con_ia(
                        texto_cv,
                        texto_oferta,
                        api_key_a_usar
                    )

                    fase = "validación de la respuesta de la IA"

                    if not isinstance(cv_generado, str):
                        raise TypeError(
                            "La IA no ha devuelto una cadena de texto. "
                            f"Tipo recibido: {type(cv_generado).__name__}"
                        )

                    if not cv_generado.strip():
                        raise ValueError(
                            "La IA ha devuelto una respuesta vacía."
                        )

                    st.session_state.cv_html = cv_generado

                    if not api_key_usuario.strip():
                        usos_guardados += 1
                        cookies.set(
                            COOKIE_USOS,
                            str(usos_guardados)
                        )

                    st.success("🎉 ¡Tu CV ha sido adaptado!")

            except Exception as exc:

                # Registra el error completo en los logs de Render.
                logging.exception(
                    "ERROR EN EL PROCESAMIENTO DEL CV. Fase: %s",
                    fase
                )

                if "429" in str(exc):
                    st.error(
                        "🛑 Se ha alcanzado el límite temporal de la API. "
                        "Inténtalo más tarde o utiliza tu propia API Key."
                    )
                else:
                    st.error(
                        f"No se pudo completar el proceso durante: {fase}. "
                        "Consulta los registros del servidor."
                    )

# ---------------------------------------------------------------------
# Vista previa y descarga CV nativo
# ---------------------------------------------------------------------
def generar_pdf_desde_html(codigo_html):
    """
    Convierte un string HTML/CSS en un archivo PDF binario indexable (ATS-Friendly)
    con dimensiones de página A4 estrictas y márgenes profesionales congelados.
    """
    estilos_pdf = """
    <style>
        @page {
            size: a4;
            margin: 1.2cm; /* Margen profesional estrecho para asegurar 1 página */
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 10pt; /* TAMAÑO DE LETRA 10 EXIGIDO POR REQUISITO */
            line-height: 1.35;
            color: #2b2b2b;
        }
        h3 {
            font-size: 11.5pt;
            font-weight: bold;
            margin-top: 14px;
            margin-bottom: 4px;
            color: #4A1525; /* Color Guinda/Vino premium de texto sin líneas divisorias */
            text-transform: uppercase;
        }
        p {
            margin-top: 0px;
            margin-bottom: 4px;
            text-align: left; /* ALINEACIÓN ESTRICTA A LA IZQUIERDA PARA ATS */
        }
    </style>
    """
    html_completo = f"<html><head>{estilos_pdf}</head><body>{codigo_html}</body></html>"
    
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_completo, dest=buffer)
    buffer.seek(0)
    return buffer if not pisa_status.err else None

# Renderizado final en la interfaz
if 'cv_html' in st.session_state and st.session_state['cv_html']:
    st.write("### 💼 Vista previa de tu CV Optimizado")
    
    # 1. Mostramos la hoja blanca estética simulando el folio A4 real en el navegador
    plantilla_estetica_ats = f"""
    <div style="
        background-color: #ffffff; 
        color: #333333; 
        font-family: 'Helvetica', 'Arial', sans-serif; 
        font-size: 10.5pt; 
        line-height: 1.5; 
        padding: 40px; 
        border: 1px solid #d0d0d0; 
        border-radius: 6px;
        max-width: 800px;
        margin: 0 auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    ">
        {st.session_state['cv_html']}
    </div>
    """
    st.html(plantilla_estetica_ats)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Compilación directa a PDF en el servidor con xhtml2pdf
    if pisa:
        with st.spinner("Compilando tu PDF oficial para ATS..."):
            pdf_final = generar_pdf_desde_html(st.session_state['cv_html'])
            
            if pdf_final:
                st.download_button(
                    label="💾 Descargar CV en Formato PDF Oficial para ATS",
                    data=pdf_final,
                    file_name="CV_Optimizado_ATS.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("⚠️ Hubo un problema al procesar el formato del PDF en el servidor.")
    else:
        st.error("⚠️ La librería xhtml2pdf no se cargó correctamente. Revisa la instalación.")
