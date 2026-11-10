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
        "Eres un sistema experto y automatizado de optimización de currículums para filtros ATS y reclutadores.\n\n"
        
         "REGLAS OBLIGATORIAS DE CONTENIDO (CONSERVACIÓN Y FILTRADO):\n"
        "1. DATOS DE CONTACTO COMPLETOS: Mantén intactos en la parte superior el Nombre Completo, Apellidos, "
        "Teléfono, Email y los enlaces web (GitHub, LinkedIn, portafolios) del CV original.\n"
        "2. HABILIDADES TÉCNICAS (MÁXIMO 10): Filtra la lista masiva de tecnologías del usuario y selecciona "
        "ÚNICA Y EXCLUSIVAMENTE un máximo de 10 habilidades técnicas estratégicas para la Oferta de Empleo. "
        "Elimina el resto por completo de esta sección para evitar saturación (keyword stuffing).\n"
        "3. PROHIBICIÓN DE DUPLICADOS (SIN SECCIÓN APTITUDES): Está terminantemente prohibido crear una sección "
        "llamada 'APTITUDES' o repetir herramientas secundarias abajo si ya se ha listado el bloque de habilidades "
        "técnicas principales. Unifica o descarta el exceso.\n"
        "4. INTEGRIDAD DE DATOS REALES: Conserva los nombres de cursos, bootcamps, horas de formación y certificaciones.\n"
        "5. HONESTIDAD TOTAL: Prohibido inventar números, métricas o porcentajes que no existan en el original.\n"
        "6. PERFIL PROFESIONAL COMPACTO: El resumen profesional inicial debe tener un máximo de 3 líneas.\n"
        "7. SIN RELLENOS: No añadas 'Referencias', notas de la IA, saludos, ni frases de cortesía.\n\n"
        
        "REGLAS CRÍTICAS DE FORMATO (PROHIBICIÓN DE SÍMBOLOS):\n"
        "- ESTÁ PROHIBIDO EL USO DE GUIONES ('-'), asteriscos o cualquier tipo de viñeta para listar elementos.\n"
        "- Escribe las funciones, logros o habilidades técnicas como palabras sueltas o párrafos normales, "
        "separados únicamente por saltos de línea estándar.\n"
        "- NO utilices sintaxis Markdown (sin asteriscos '**', sin almohadillas '#').\n"
        "- NO utilices etiquetas HTML complejas.\n"
        "- Usa una línea en blanco y escribe los títulos de las secciones en MAYÚSCULAS para estructurar el documento "
        "(ej. HABILIDADES TÉCNICAS)."
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
