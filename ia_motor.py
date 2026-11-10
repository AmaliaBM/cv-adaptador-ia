import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Adapta un CV a una oferta de empleo mediante Groq de forma limpia para ATS.
    """
    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    if not texto_cv or not texto_cv.strip():
        raise ValueError("El currículum está vacío.")

    if not texto_oferta or not texto_oferta.strip():
        raise ValueError("La oferta de empleo está vacía.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema = (
        "Eres un consultor experto en reclutamiento y marca profesional. Tu objetivo es reescribir y adaptar "
        "el currículum del usuario para que encaje perfectamente con los requisitos de la oferta de empleo.\n\n"
        
        "REGLAS ESTRICTAS DE REDACCIÓN Y SEGURIDAD:\n"
        "1. HONESTIDAD TOTAL Y MÉTRICAS REALES: Prohibido terminantemente inventar empresas, títulos, tecnologías "
        "o métricas cuantitativas (como inventar porcentajes de optimización del 20% o 30% si no venían explícitos "
        "en el currículum original). Optimiza explicando los logros reales mediante el Método STAR sin alterar los datos.\n"
        "2. CONSERVACIÓN DE DATOS ÚTILES: Mantén intacta toda la información esencial de contacto, nombres de tecnologías, "
        "teléfonos, correos, certificaciones y datos numéricos originales.\n"
        "3. PROHIBICIÓN DE MARKDOWN: Está estrictamente prohibido usar caracteres de marcado Markdown. No uses asteriscos "
        "('**' o '*') para negritas/cursivas, ni almohadillas ('#', '##') para encabezados. Estructura los títulos escribiéndolos "
        "en mayúsculas en una línea independiente seguida de un salto de línea.\n"
        "4. RESALTADO EXCLUSIVO (HTML SPAN): La ÚNICA etiqueta permitida en tu respuesta es envolver las palabras clave, términos "
        "o frases optimizadas entre las etiquetas: <span style='background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 4px; font-weight: 500;'> y </span>. "
        "No uses listas HTML (<ul>, <li>), ni tablas, ni columnas, ni elementos decorativos.\n"
        "5. PROHIBICIÓN DE COMENTARIOS Y AUTOPROMOCIÓN: Devuelve única y exclusivamente el texto adaptado del currículum. "
        "No incluyas comentarios iniciales ni finales explicando lo que hiciste (ej: 'Aquí tienes tu CV adaptado...'). "
        "No incluyas secciones artificiales de análisis como 'Alineación con la empresa'."
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

    if not completation.choices:
        raise RuntimeError("Groq no ha devuelto ninguna respuesta.")

    respuesta = completation.choices[0].message.content

    if not respuesta or not respuesta.strip():
        raise RuntimeError("Groq ha devuelto una respuesta vacía.")

    return respuesta.strip()
