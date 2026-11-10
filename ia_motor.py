import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Se conecta a Groq para adaptar el CV devolviendo una estructura HTML limpia
    lista para ser convertida en un PDF ATS-Friendly rígido.
    """
    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema = (
        "Eres un sistema experto en optimización de currículums para filtros ATS y reclutadores.\n\n"
        "Tu objetivo es reescribir el CV del usuario adaptándolo a la oferta, devolviendo el resultado "
        "únicamente en texto estructurado con etiquetas HTML básicas de bloque (<h3>, <p>). "
        "Está terminantemente prohibido usar Markdown (sin '**', sin '#').\n\n"
        "REGLAS DE CONTENIDO STRICTORAS:\n"
        "1. DATOS DE CONTACTO: Mantén Nombre, Apellidos, Teléfono, Email, GitHub y LinkedIn en la parte superior.\n"
        "2. FILTRADO DE PROYECTOS: Incluye un máximo de 3 proyectos, los más relevantes para la oferta.\n"
        "3. HONESTIDAD TOTAL: Prohibido inventar porcentajes, números o métricas que no existan en el original.\n"
        "4. SIN RELLENOS: No añadas la sección 'Referencias', notas de la IA ni saludos.\n"
        "5. SIN VIÑETAS: No uses guiones ni asteriscos para listas. Escribe los logros como frases continuas dentro de etiquetas <p>.\n\n"
        "Estructura el documento usando <h3> para los títulos de sección (ej: <h3>EXPERIENCIA PROFESIONAL</h3>) "
        "y <p> para los textos y datos de contacto."
    )

    contenido_usuario = f"OFERTA DE EMPLEO:\n{texto_oferta}\n\nCURRÍCULUM ACTUAL:\n{texto_cv}"

    completation = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": contenido_usuario}
        ],
        temperature=0.3,
        max_tokens=3000
    )

    return completation.choices[0].message.content.strip()

