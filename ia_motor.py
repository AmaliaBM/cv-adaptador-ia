
from groq import Groq


def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Adapta un CV a una oferta de empleo mediante Groq.
    Devuelve el contenido generado por la IA.
    """

    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    if not texto_cv or not texto_cv.strip():
        raise ValueError("El currículum está vacío.")

    if not texto_oferta or not texto_oferta.strip():
        raise ValueError("La oferta de empleo está vacía.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema = (
        "Eres un motor automatizado y estricto de optimización de currículums para sistemas ATS.\n\n"
        
        "REGLAS DE CONTENIDO CRÍTICAS:\n"
        "1. HONESTIDAD ABSOLUTA (PROHIBIDO INVENTAR MÉTRICAS): No inventes NINGÚN porcentaje, número, "
        "métrica de éxito, fecha o nombre de empresa que no esté explícitamente en el CV original. Si el usuario "
        "no proporciona un número (ej. '%'), tú NO debes crearlo. Optimiza usando sus datos reales.\n"
        "2. SIN TEXTO COMPLEMENTARIO NI RELLENO: No añadas secciones genéricas como 'Referencias', 'Disponibilidad' "
        "ni frases de cortesía al inicio o al final. No saludes ni des explicaciones de lo que has hecho.\n"
        "3. PERFIL PROFESIONAL ULTRA-COMPACTO: El resumen profesional inicial debe tener una extensión máxima de 3 líneas.\n"
        "4. PALABRAS CLAVE: Adapta los nombres de las tecnologías y metodologías para que coincidan exactamente con "
        "los términos técnicos utilizados en la Oferta de Empleo proporcionada.\n\n"
        
        "REGLAS DE FORMATO ESTRICTAS:\n"
        "- NO uses sintaxis Markdown (sin asteriscos '**', sin almohadillas '#').\n"
        "- NO uses etiquetas HTMLcomplejas.\n"
        "- Para separar secciones, usa una línea en blanco y escribe el título de la sección en MAYÚSCULAS "
        "(ej. EXPERIENCIA PROFESIONAL).\n"
        "- Para los logros, utiliza única y exclusivamente un guion normal '-' al inicio de la línea."
    )

    contenido_usuario = (
        f"OFERTA DE EMPLEO:\n{texto_oferta}\n\n"
        f"CURRÍCULUM ACTUAL:\n{texto_cv}"
    )

    completation = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": contenido_usuario}
        ],
        temperature=0.3,
        max_tokens=3000
    )

    # IMPORTANTE: choices es una lista.
    if not completation.choices:
        raise RuntimeError("Groq no ha devuelto ninguna respuesta.")

    respuesta = completation.choices[0].message.content

    if not respuesta or not respuesta.strip():
        raise RuntimeError("Groq ha devuelto una respuesta vacía.")

    return respuesta.strip()
