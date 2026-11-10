import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Adapta un CV a una oferta de empleo mediante Groq.
    Garantiza la preservación de datos de contacto y prohíbe el uso de guiones o viñetas.
    """
    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema = (
        "Eres un sistema experto y automatizado de optimización de currículums para filtros ATS y reclutadores.\n\n"
        
        "REGLAS OBLIGATORIAS DE CONTENIDO (CONSERVACIÓN DE INFORMACIÓN):\n"
        "1. DATOS DE CONTACTO COMPLETOS: Debes mantener intactos y en la parte superior del documento el Nombre Completo, "
        "Apellidos, Teléfono, Email y los enlaces web (GitHub, LinkedIn, portafolios) que aparezcan en el CV original.\n"
        "2. INTEGRIDAD DE DATOS REALES: Conserva todas las tecnologías, nombres de cursos, bootcamps, horas de formación, "
        "certificaciones, herramientas y habilidades del CV original. No omitas información técnica valiosa.\n"
        "3. HONESTIDAD TOTAL: Está terminantemente prohibido inventar números, métricas, porcentajes (ej. % de éxito o reducción) "
        "o experiencias que no existan en el texto del currículum original.\n"
        "4. PERFIL PROFESIONAL: Adapta el resumen profesional inicial para alinearlo con las palabras clave de la oferta de empleo, "
        "con una extensión máxima de 3 líneas.\n"
        "5. SIN RELLENOS: No añadas secciones de 'Referencias', notas de la IA, saludos, ni frases de cortesía.\n\n"
        
        "REGLAS CRÍTICAS DE FORMATO (PROHIBICIÓN DE SÍMBOLOS):\n"
        "- ESTÁ PROHIBIDO EL USO DE GUIONES ('-'), asteriscos o cualquier tipo de viñeta o carácter decorativo para listar elementos.\n"
        "- En su lugar, escribe las funciones, responsabilidades o logros como párrafos normales y directos, separados únicamente por un salto de línea.\n"
        "- NO utilices sintaxis Markdown (sin asteriscos '**', sin almohadillas '#').\n"
        "- NO utilices etiquetas HTML complejas.\n"
        "- Usa una línea en blanco y escribe los títulos de las secciones en MAYÚSCULAS para estructurar el documento "
        "(ej. EXPERIENCIA PROFESIONAL)."
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
