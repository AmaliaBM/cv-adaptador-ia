import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Adapta un CV a una oferta de empleo mediante Groq.
    Genera un diseño estructurado horizontal de alta gama para ATS,
    siguiendo un patrón exacto sin símbolos divisorios ni guiones.
    """
    if not api_key or not api_key.strip():
        raise ValueError("No se ha proporcionado una API Key de Groq.")

    client = Groq(api_key=api_key.strip())

    prompt_sistema =     prompt_sistema = (
        "Eres un sistema experto de optimización estructural de currículums para filtros ATS. "
        "Tu objetivo es generar un documento ultra-compacto diseñado estrictamente para ocupar UNA SOLA PÁGINA en Word.\n\n"
        
        "REGLAS DE RECORTE DE CONTENIDO (MÁXIMA COMPRESIÓN):\n"
        "1. DATOS DE CONTACTO: Escribe los datos en un formato horizontal ultra-compacto:\n"
        "   [NOMBRE Y APELLIDOS]\n"
        "   [ROL PROFESIONAL ADAPTADO A LA OFERTA]\n"
        "   [Ciudad, País] | [Teléfono] | [Email] | GitHub: [Enlace] | LinkedIn: [Enlace]\n"
        "2. FILTRADO EXTENSIVO DE PROYECTOS (MÁXIMO 2): Selecciona única y exclusivamente los 2 proyectos más importantes y afines a la oferta. Elimina por completo todos los demás proyectos del currículum.\n"
        "3. LÍMITE DE EDUCACIÓN: Muestra un máximo de 3 títulos o bootcamps. Consensa cada titulación en una sola línea (ej. Titulación | Escuela | Fechas).\n"
        "4. SIN RELLENOS: No añadas resúmenes de perfil largos (máximo 2 líneas), secciones de 'Referencias', notas de la IA, saludos, ni 'Otras Formaciones'.\n"
        "5. HONESTIDAD TOTAL: Prohibido inventar números, fechas, porcentajes o métricas que no existan en el original.\n\n"
        
        "REGLAS DE FORMATO HORIZONTAL:\n"
        "- ESTÁ PROHIBIDO EL USO DE GUIONES ('-'), asteriscos o cualquier tipo de viñeta.\n"
        "- DESCRIPCIÓN DE EXPERIENCIAS Y PROYECTOS: Inmediatamente debajo de la metadata del puesto (Empresa | Ciudad | Fechas), escribe las funciones y logros como UN ÚNICO PÁRRAFO CONTINUO DE MÁXIMO 2 LÍNEAS. No desgloses en múltiples líneas.\n"
        "- TECHNICAL SKILLS: Agrupa las tecnologías por categorías semánticas en líneas horizontales seguidas por dos puntos y separadas por comas. Ejemplo: 'Programming: Java, JavaScript. Databases: MongoDB. DevOps: Docker.' (Máximo 3 líneas en total para toda la sección).\n"
        "- IDIOMAS Y SOFT SKILLS: Una única línea horizontal por sección utilizando barras verticales '|' como separadores.\n"
        "- NO utilices sintaxis Markdown (sin '**', sin '#'). Separa las secciones únicamente con una línea en blanco y el título en MAYÚSCULAS."
    )

    contenido_usuario = (
        f"OFERTA DE EMPLEO:\n{texto_oferta}\n\n"
        f"CURRÍCULUM ACTUAL:\n{texto_cv}"
    )

    completation = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "system_prompt" if "system_prompt" in dir(client) else "content": prompt_sistema},
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
