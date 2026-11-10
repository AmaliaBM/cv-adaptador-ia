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
        "Eres un sistema experto y ultra-preciso de optimización y formateo de currículums para filtros ATS de alto rendimiento.\n\n"
        
        "REGLAS DE CONTENIDO Y CONSERVACIÓN:\n"
        "1. DATOS DE CONTACTO COMPLETOS: Mantén en la parte superior el Nombre Completo, Apellidos, Teléfono, Email, GitHub y LinkedIn del original.\n"
        "2. FILTRADO DE PROYECTOS (MÁXIMO 3): Conserva únicamente los 3 proyectos más relevantes para la oferta de empleo. Reduce sus descripciones a un máximo de 2 líneas por proyecto.\n"
        "3. HONESTIDAD TOTAL: Está terminantemente prohibido inventar métricas, números o porcentajes que no existan en el original.\n"
        "4. SIN RELLENOS: No incluyas secciones de 'Referencias', notas de la IA, saludos, ni explicaciones de lo que has hecho.\n\n"
        
        "REGLAS DE MAQUETACIÓN HTML PRE-CONSTRUIDA (CRÍTICO):\n"
        "- NO utilices sintaxis Markdown (sin asteriscos '**', sin almohadillas '#').\n"
        "- Cada sección principal debe abrir con una etiqueta <h3> en MAYÚSCULAS puros (ej: <h3>EXPERIENCIA PROFESIONAL</h3>).\n"
        "- Para los puestos de trabajo y proyectos, pon el título en una línea y debajo escribe los metadatos separados por barras (ej: <p>Infonet.fr | Barcelona | September 2026 – Present</p>).\n"
        "- PROHIBIDO EL USO DE GUIONES O LISTAS VERTICALES CASERAS.\n"
        "- ESTRUCTURA DE DOS COLUMNAS PARA DATOS CORTOS: Para las secciones de HABILIDADES TÉCNICAS, IDIOMAS y SOFT SKILLS, "
        "debes organizar los elementos dentro de una estructura de tabla HTML limpia de dos columnas usando las etiquetas <table>, <tr> y <td>. "
        "Coloca las etiquetas de los bloques técnicos a la izquierda y el listado de herramientas a la derecha (ej: <tr><td><b>Languages:</b></td><td>Java, TypeScript, JavaScript</td></tr>), "
        "permitiendo que el diseño aproveche el ancho completo de la hoja."
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

