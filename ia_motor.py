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
        "ÚNICA Y EXCLUSIVAMENTE un máximo de 10 habilidades técnicas. Elige las 10 herramientas, lenguajes o frameworks "
        "que tengan mayor coincidencia y valor estratégico con respecto a la Oferta de Empleo proporcionada. "
        "Elimina el resto por completo de esta sección para evitar saturación (keyword stuffing).\n"
        "3. INTEGRIDAD DE DATOS REALES: Conserva los nombres de cursos, bootcamps, horas de formación, certificaciones "
        "y datos de la sección de educación y experiencia.\n"
        "4. HONESTIDAD TOTAL: Está terminantemente prohibido inventar números, métricas, porcentajes o experiencias "
        "que no existan en el texto del currículum original.\n"
        "5. PERFIL PROFESIONAL COMPACTO: El resumen profesional inicial debe alinearse con la oferta con un máximo de 3 líneas.\n"
        "6. SIN RELLENOS: No añadas secciones de 'Referencias', notas de la IA, saludos, ni frases de cortesía.\n\n"
        
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
