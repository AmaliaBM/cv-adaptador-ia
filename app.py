import streamlit as st
import re
import random
import time
import os
from streamlit_cookies_controller import CookieController
from lector_pdf import extraer_texto_pdf
from ia_motor import adaptar_cv_con_ia

# Configuración de la página web
st.set_page_config(
    page_title="Adaptador de CV Solidario",
    page_icon="💼",
    layout="wide"
)

# 1. CONTROL DE NAVEGACIÓN Y ANTIBOTS
if 'verificado_humano' not in st.session_state:
    st.session_state['verificado_humano'] = False

# Inicializar de forma segura la variable del CV para evitar KeyError en Render
if 'cv_html' not in st.session_state:
    st.session_state['cv_html'] = None

# Inicializar números del captcha si no existen
if 'captcha_num1' not in st.session_state:
    st.session_state['captcha_num1'] = random.randint(1, 9)
    st.session_state['captcha_num2'] = random.randint(1, 9)
    st.session_state['captcha_resultado'] = st.session_state['captcha_num1'] + st.session_state['captcha_num2']
    st.session_state['captcha_inicio_tiempo'] = time.time()

# Inicializamos el controlador de cookies del navegador
cookies = CookieController()
usos_guardados = cookies.get('cv_usos_gratuitos')
usos_guardados = int(usos_guardados) if usos_guardados is not None else 0

# LÓGICA DE CONTROL HÍBRIDA CON MANEJO DE EXCEPCIONES PARA RENDER
api_key_servidor = None

try:
    # 1. Intentamos leer desde el sistema nativo de secretos de Streamlit (Local)
    if "GROQ_API_KEY" in st.secrets:
        api_key_servidor = st.secrets["GROQ_API_KEY"]
except Exception:
    # 2. Si st.secrets no existe o lanza un error (como en Render), pasamos silenciosamente
    pass

# 3. Si no se encontró en st.secrets, buscamos en las Variables de Entorno del sistema operativo (Render)
if not api_key_servidor and os.environ.get("GROQ_API_KEY"):
    api_key_servidor = os.environ.get("GROQ_API_KEY")

def limpiar_html_para_txt(texto_html):
    """Elimina etiquetas HTML para compatibilidad con sistemas ATS."""
    if not texto_html:
        return ""
    patron_html = re.compile(r'<[^>]+>')
    return patron_html.sub('', texto_html)


# =========================================================================
# ESCENARIO A: PANTALLA DE VERIFICACIÓN ANTIBOTS (ACCESO PRINCIPAL)
# =========================================================================
if not st.session_state['verificado_humano']:
    
    # Calcular el tiempo transcurrido desde la generación del reto actual (Límite: 30 segundos)
    tiempo_limite = 30
    tiempo_transcurrido = time.time() - st.session_state['captcha_inicio_tiempo']
    tiempo_restante = max(0, int(tiempo_limite - tiempo_transcurrido))
    
    # Si el tiempo expira, regeneramos los números de forma controlada al interactuar
    if tiempo_restante <= 0:
        st.session_state['captcha_num1'] = random.randint(1, 9)
        st.session_state['captcha_num2'] = random.randint(1, 9)
        st.session_state['captcha_resultado'] = st.session_state['captcha_num1'] + st.session_state['captcha_num2']
        st.session_state['captcha_inicio_tiempo'] = time.time()
        tiempo_restante = tiempo_limite
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_inf, col_box, col_sup = st.columns(3)
    
    with col_box:
        st.markdown(
            "<div style='text-align: center;'><h2>🛡️ Verificación de Seguridad</h2>"
            "<p>Por favor, confirma que eres un humano para acceder a la herramienta solidaria.</p></div>",
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # Desafío matemático (ÚNICO espacio de escritura estable en pantalla)
        mensaje_captcha = f"¿Cuánto es {st.session_state['captcha_num1']} + {st.session_state['captcha_num2']}?"
        respuesta_usuario = st.number_input(mensaje_captcha, step=1, value=0, key="unico_input_captcha")
        
        # Visualizador de tiempo restante estilo Google (Barra de progreso fija por ciclo)
        st.write(f"⏳ Este código de seguridad expira en aproximadamente: **{tiempo_restante} segundos**")
        st.progress(tiempo_restante / tiempo_limite)
        
        st.markdown("<br>", unsafe_allow_html=True)
        boton_acceder = st.button("🔓 Verificar y Entrar", type="primary", use_container_width=True)
        
        if boton_acceder:
            # Control básico de velocidad para evitar clicks automáticos en milisegundos
            if tiempo_transcurrido < 1.0:
                st.error("🛑 Procesamiento demasiado rápido. Resuelve la operación con calma.")
            elif respuesta_usuario != st.session_state['captcha_resultado']:
                st.error("🛑 El resultado de la operación es incorrecto. Inténtalo de nuevo.")
            else:
                # Éxito: Autorizado
                st.session_state['verificado_humano'] = True
                st.rerun()
                
    st.stop()  # Detiene la carga de la aplicación si el usuario no está verificado


# =========================================================================
# ESCENARIO B: APLICACIÓN PRINCIPAL (ACCESO CONCEDIDO)
# =========================================================================

# TÍTULO Y DESCRIPCIÓN
st.title("💼 Adaptador de CV con IA (100% Gratuito)", anchor=False)
st.subheader("Optimiza tu currículum para la oferta de empleo que deseas", anchor=False)
st.write(
    "Esta herramienta analiza los requisitos de la empresa y adapta estratégicamente tu perfil. "
    "Las secciones resaltadas en amarillo representan las mejoras, palabras clave y optimizaciones "
    "añadidas a tu CV para alinearlo con la oferta de empleo y convencer a los reclutadores."
)

st.divider()

# BARRA LATERAL: CONFIGURACIÓN, PRIVACIDAD Y TUTORIAL
with st.sidebar:
    st.header("🔑 Configuración y Llave de IA", anchor=False)
    
    if usos_guardados < 1:
        st.success("✨ Tienes 1 uso de prueba gratuito activado de forma solidaria.")
        api_key_usuario = st.text_input("🔑 Introduce tu propia API Key de Groq (Opcional para el primer uso):", type="password")
        api_key_a_usar = api_key_usuario if api_key_usuario.strip() else api_key_servidor
    else:
        st.warning("⏳ Has usado tu prueba solidaria en este equipo. Introduce tu propia API Key para seguir gratis:")
        api_key_usuario = st.text_input("🔑 Introduce tu API Key de Groq:", type="password")
        api_key_a_usar = api_key_usuario

    with st.expander("💡 Guía rápida: Consigue tu API Key gratis en 30 segundos"):
        st.markdown(
            "Para evitar que la herramienta se sature y que puedas usarla **de forma ilimitada** sin coste, "
            "puedes usar tu propia clave siguiendo estos pasos:\n\n"
            "1. Entra en la web oficial gratuita: **[Groq Cloud Console](https://groq.com)**\n"
            "2. Inicia sesión con tu cuenta de Google o correo.\n"
            "3. En el menú izquierdo, haz clic en **API Keys**.\n"
            "4. Pulsa el botón **Create API Key**, dale cualquier nombre y copia el código largo generado.\n"
            "5. Pégalo en el cuadro de texto de aquí arriba."
        )
        
    with st.expander("🔒 Tu Privacidad es lo Primero"):
        st.markdown(
            "- **Sin Registros:** Eres 100% anónimo.\n"
            "- **Procesamiento Volátil:** No guardamos tus datos en el servidor. Al cerrar la pestaña del navegador, se borran automáticamente.\n"
            "- **Cookies Técnicas:** Guardamos una cookie local en tu navegador exclusivamente para controlar el límite de cortesía del primer uso diario."
        )

# PANTALLA PRINCIPAL: FORMULARIOS
col1, col2 = st.columns(2)

with col1:
    st.header("1. Tus Datos", anchor=False)
    archivo_subido = st.file_uploader("Sube tu CV actual en formato PDF", type=["pdf"])
    texto_oferta = st.text_area(
        "Pega aquí la descripción de la oferta de empleo (requisitos, tareas, etc.):",
        height=350,
        placeholder="Ej: Buscamos un desarrollador Python con experiencia en Django..."
    )

with col2:
    st.header("2. CV Adaptado", anchor=False)
    boton_adaptar = st.button("✨ Adaptar Currículum Ahora", type="primary")
    
    if boton_adaptar:
        if not api_key_a_usar:
            st.error("⚠️ Para continuar, por favor introduce tu propia API Key de Groq en la barra lateral.")
        elif not archivo_subido:
            st.error("⚠️ Por favor, sube tu currículum en PDF.")
        elif not texto_oferta.strip():
            st.error("⚠️ Por favor, pega la oferta de empleo.")
        else:
            with st.spinner("Analizando la oferta y adaptando tu CV de manera estratégica..."):
                texto_cv = extraer_texto_pdf(archivo_subido)
                
                if "Error al leer" in texto_cv:
                    st.error(texto_cv)
                else:
                    try:
                        cv_generado = tratar_cv_con_ia = adaptar_cv_con_ia(texto_cv, texto_oferta, api_key_a_usar)
                        
                        if cv_generado.strip():
                            st.session_state['cv_html'] = cv_generado
                            
                            if not api_key_usuario.strip():
                                usos_guardados += 1
                                cookies.set('cv_usos_gratuitos', usos_guardados)
                                
                            st.success("🎉 ¡Tu CV ha sido adaptado!")
                        else:
                            st.error("⚠️ La IA devolvió una respuesta vacía. Por favor, inténtalo de nuevo.")
                            
                    except Exception as e:
                        if "429" in str(e):
                            st.error(
                                "🛑 Se han agotado los tokens disponibles para esta clave en este momento. "
                                "Introduce tu propia API Key en la barra lateral para saltarte este límite."
                            )
                        else:
                            st.error(f"Hubo un problema con la IA: {str(e)}")

    # RENDERIZADO Y DESCARGA
    if 'cv_html' in st.session_state and st.session_state['cv_html']:
        st.write("### Vista Previa de Cambios:")
st.html(st.session_state['cv_html'])
st.divider()
cv_texto_plano = limpiar_html_para_txt(st.session_state['cv_html'])
st.download_button(
label="💾 Descargar CV en Texto Plano Limpio (.txt)",
data=cv_texto_plano,
file_name="CV_Optimizado_ATS.txt",
mime="text/plain",
use_container_width=True
);