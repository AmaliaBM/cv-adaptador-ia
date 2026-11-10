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
        "Eres un sistema experto y ultra-estricto de optimización estructural de currículums para filtros ATS de alto rendimiento. "
        "Tu único objetivo es generar un documento compacto diseñado específicamente para ocupar UNA SOLA PÁGINA real.\n\n"
        
        "REGLAS DE SELECCIÓN Y RECORTE DE CONTENIDO (MÁXIMA COMPRESIÓN):\n"
        "1. CABECERA COMPACTA: Escribe los datos de contacto en un único bloque de texto sin separar por párrafos independientes. "
        "Usa el formato horizontal exacto: [Nombre] | [Teléfono] | [Email] | GitHub: [Enlace] | LinkedIn: [Enlace] | [Ubicación].\n"
        "2. FILTRADO DE PROYECTOS (MÁXIMO 2): Selecciona únicamente los 2 proyectos más importantes y afines a la oferta. Elimina el resto.\n"
        "3. LÍMITE DE EDUCACIÓN: Muestra un máximo de 3 títulos o bootcamps. Cada uno debe ocupar una sola línea limpia.\n"
        "4. HONESTIDAD TOTAL: Prohibido inventar números, fechas, porcentajes o métricas que no existan en el original.\n"
        "5. PROHIBICIÓN DE SECCIONES FINALES: No incluyas NUNCA secciones de 'Referencias', 'Alineación con la empresa', notas de la IA, saludos, ni resúmenes explicativos al final. El documento debe terminar en la sección de habilidades.\n\n"
        
        "REGLAS DE FORMATO (PROHIBICIÓN DE SÍMBOLOS):\n"
        "- ESTÁ TOTALMENTE PROHIBIDO EL USO DE GUIONES ('-'), asteriscos o cualquier tipo de viñeta.\n"
        "- Escribe las funciones y logros como un único párrafo continuo de máximo 2 líneas por experiencia.\n"
        "- NO utilices sintaxis Markdown (sin '**', sin '#', sin '###').\n"
        "- Estructura el documento usando únicamente <h3> para los títulos de sección (ej: <h3>EXPERIENCIA PROFESIONAL</h3>) "
        "y <p> para los bloques de texto normal."
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

