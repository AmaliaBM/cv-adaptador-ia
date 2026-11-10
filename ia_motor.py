import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Adapta un CV a una oferta de empleo mediante Groq.
    Garantiza la preservación de datos de contacto, prohíbe guiones
    y limita estrictamente a un máximo de 10 habilidades técnicas.
    """
    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema = (
        "Eres un sistema experto y automatizado de optimización de currículums para filtros ATS y reclutadores. "
        "Tu objetivo es generar un documento ultra-compacto diseñado específicamente para encajar en UNA SOLA PÁGINA real al ser pegado en Word.\n\n"
        
        "REGLAS DE CONTENIDO Y RESTRICCIÓN DE LONGITUD (CRÍTICAS):\n"
        "1. DATOS DE CONTACTO: Mantén intactos en la parte superior el Nombre Completo, Apellidos, Teléfono, Email y los enlaces web (GitHub, LinkedIn) en líneas compactas.\n"
        "2. FILTRADO ESTRICTO DE PROYECTOS (MÁXIMO 3): Selecciona única y exclusivamente los 3 proyectos más relevantes y con mayor afinidad técnica con la oferta de empleo. Elimina por completo los demás proyectos del documento.\n"
        "3. LÍMITES EN EDUCACIÓN: Agrupa las formaciones de manera compacta. Si hay demasiadas, conserva solo las 3 titulaciones o bootcamps más importantes para el puesto.\n"
        "4. HONESTIDAD TOTAL: Prohibido inventar números, fechas, porcentajes o métricas que no existan en el original.\n"
        "5. SIN RELLENOS: No añadas secciones de 'Referencias', 'Otras Formaciones', ni comentarios de cortesía.\n\n"
        
        "REGLAS DE FORMATO HORIZONTAL PARA AHORRO DE ESPACIO:\n"
        "- PROHIBIDO EL USO DE LISTAS VERTICALES, GUIONES ('-') O VIÑETAS.\n"
        "- SECCIÓN HABILIDADES TÉCNICAS: Debes seleccionar un máximo de 10 tecnologías y escribirlas en UNA SOLA LÍNEA HORIZONTAL, separadas por comas (ej. HABILIDADES TÉCNICAS: Java, Angular, TypeScript...).\n"
        "- SECCIÓN IDIOMAS: Escríbelos en una sola línea horizontal separados por comas.\n"
        "- SECCIÓN HABILIDADES BLANDAS: Selecciona un máximo de 5 y escríbelas en una sola línea horizontal separadas por comas.\n"
        "- Escribe las descripciones de la experiencia y los proyectos como párrafos continuos muy breves (máximo 2 líneas por experiencia o proyecto).\n"
        "- NO utilices sintaxis Markdown (sin '**', sin '#'). Las secciones se separan con una línea en blanco y el título en MAYÚSCULAS."
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
