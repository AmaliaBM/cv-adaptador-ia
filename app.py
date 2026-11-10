import logging
import os
import random
import re
import time
from html.parser import HTMLParser
from io import BytesIO
from xml.sax.saxutils import escape

import streamlit as st
from streamlit_cookies_controller import CookieController

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
    """Limpia profundamente HTML, Markdown, enlaces y comentarios finales."""
    if not texto_html:
        return ""
    
    # 1. Eliminar etiquetas HTML completas
    texto = re.compile(r'<[^>]+>').sub('', texto_html)
    
    # 2. Eliminar residuos de etiquetas HTML cortadas al final
    texto = re.compile(r'</?[a-zA-Z]*\s*$').sub('', texto)
    
    # 3. Eliminar marcadores de Markdown comunes (negritas) sin romper palabras
    texto = texto.replace('**', '').replace('__', '')
    
    # 4. Eliminar almohadillas de encabezados (#, ##) al inicio de las líneas
    texto = re.compile(r'^#+\s+', re.MULTILINE).sub('', texto)
    
    # 5. Limpiar formatos de enlaces Markdown [Texto](URL) dejando solo el Texto
    texto = re.compile(r'\[([^\]]+)\]\([^\)]+\)').sub(r'\1', texto)
    
    # 6. Cortar comentarios finales intrusivos de la IA
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
if st.session_state.cv_html:
    st.write("### 📋 Tu CV Optimizado para ATS Listo")
    st.info("💡 Usa el botón que aparece arriba a la derecha del recuadro para copiar todo el texto con un solo clic.")
    
    # 1. Aplicamos la limpieza profunda (fuera HTML, Markdown y comentarios de la IA)
    texto_cv_limpio = limpiar_todo_para_ats(st.session_state.cv_html)

    if texto_cv_limpio:
        # 2. ENCAPSULADO EN RECUADRO CON BOTÓN DE COPIAR AUTOMÁTICO
        # Al usar st.code con language=None, Streamlit crea el recuadro gris profesional 
        # y añade el botón nativo de copiar en la esquina superior derecha.
        st.code(
            texto_cv_limpio,
            language=None, # Mantiene el texto plano sin coloreado de código de programación
            wrap_lines=True # Evita el scroll horizontal forzando saltos de línea limpios
        )
        
        st.success("🎉 ¡Proceso completado! Copia el texto y pégalo en tu editor favorito (Word, Docs) para guardarlo como PDF.")
    else:
        st.warning("La respuesta generada no contiene texto que se pueda mostrar.")

