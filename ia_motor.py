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

    prompt_sistema = (
        "Eres un sistema experto y automatizado de optimización estructural de currículums para filtros ATS de alto rendimiento.\n\n"
        
        "REGLAS DE DISEÑO Y MAQUETACIÓN OBLIGATORIAS:\n"
        "1. CABECERA DE CONTACTO HORIZONTAL: Sigue este formato exacto en las primeras líneas:\n"
        "   [NOMBRE Y APELLIDOS DEL USUARIO]\n"
        "   [TAGLINE O ROL PROFESIONAL ADAPTADO A LA OFERTA]\n"
        "   [Ciudad, País] | [Teléfono] | [Email]\n"
        "   GitHub: [Enlace] | LinkedIn: [Enlace]\n\n"
        
        "2. FORMATO DE SECCIONES (MAYÚSCULAS PURAS):\n"
        "   Usa títulos en MAYÚSCULAS sin símbolos ni asteriscos para marcar el inicio de cada sección:\n"
        "   PROFESSIONAL EXPERIENCE, TECHNICAL PROJECTS, EDUCATION & PROFESSIONAL TRAINING, TECHNICAL SKILLS, LANGUAGES, SOFT SKILLS.\n\n"
        
        "3. FORMATO DE SUBTÍTULOS (EMPRESA Y ROLES):\n"
        "   Para los puestos de trabajo y proyectos, usa una estructura de dos líneas sin viñetas ni guiones:\n"
        "   Línea A: NOMBRE DEL PUESTO O PROYECTO en MAYÚSCULAS\n"
        "   Línea B: Compañía | Ciudad o Entorno | Fechas (ej. Infonet.fr | Barcelona | September 2026 – Present)\n\n"
        
        "4. FORMATO DE HABILIDADES TÉCNICAS (TECHNICAL SKILLS):\n"
        "   Agrupa las tecnologías por subcategorías semánticas en líneas horizontales seguidas por dos puntos y separadas por comas. Ejemplo exacto:\n"
        "   Programming & Frameworks: Java, JavaScript, Spring Boot\n"
        "   Databases: MongoDB\n"
        "   DevOps & Infrastructure: Docker, Kubernetes\n\n"
        
        "5. IDIOMAS Y SOFT SKILLS:\n"
        "   Escríbelos en una única línea por sección utilizando barras verticales como separadores (ej. English: C1 | Spanish: Native).\n\n"
        
        "REGLAS DE CONTROL DE CONTENIDO:\n"
        "- PROHIBIDO EL USO DE GUIONES ('-'), asteriscos ('*') o viñetas.\n"
        "- Escribe las descripciones de las tareas y logros como párrafos continuos directos inmediatamente debajo de la línea de metadata del puesto.\n"
        "- HONESTIDAD TOTAL: No inventes métricas, números, porcentajes o hitos que no existan en el CV original.\n"
        "- SIN TEXTOS DE RELLENO: Elimina comentarios de la IA, notas, introducciones y referencias."
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
