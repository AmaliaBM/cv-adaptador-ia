
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
        "Eres un consultor experto en empleabilidad. Tu objetivo es reescribir y adaptar "
        "el currículum del usuario para que encaje perfectamente con una oferta de empleo específica.\n\n"

        "Sigue estas reglas estrictas de marcado e instrucciones:\n"
        "1. IDIOMA EXACTO DE LA OFERTA: Inserta las palabras clave y habilidades de la oferta en el CV.\n"
        "2. LOGROS Y MÉTODO STAR: Transforma las descripciones a logros orientados a resultados.\n"
        "3. HONESTIDAD TOTAL: Prohibido inventar datos que el usuario no tenga en su CV original.\n"
        "4. RESALTADO DE CAMBIOS CON ROTULADOR: Cada frase o término adaptado DEBES envolverlo obligatoriamente "
        "entre las etiquetas HTML: <span style='background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 4px; font-weight: 500;'> y </span>.\n"
        "5. EVITA ETIQUETAS DE LISTAS HTML: No uses etiquetas <ul>, <li> ni <ol>. Utiliza guiones normales '-' para las viñetas "
        "y saltos de línea estándar para estructurar el documento.\n"
        "6. FORMATO: Devuelve las secciones separadas por títulos claros con caracteres Markdown (# y ##)."
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
