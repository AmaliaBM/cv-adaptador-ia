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
        "2. FILTRADO DE PROYECTOS (MÁXIMO 3): Conserva únicamente los 3 proyectos más relevantes para la oferta de empleo. Reduce sus descripciones a un párrafo continuo de máximo 2 líneas por proyecto.\n"
        "3. HONESTIDAD TOTAL: Está terminantemente prohibido inventar métricas, números o porcentajes que no existan en el original.\n"
        "4. SIN RELLENOS: No incluyas secciones de 'Referencias', notas de la IA, saludos, ni explicaciones de lo que has hecho.\n\n"
        
        "REGLAS DE MAQUETACIÓN EN UNA SOLA COLUMNA (CRÍTICO PARA ATS):\n"
        "- ESTÁ TOTALMENTE PROHIBIDO EL USO DE TABLAS (<table>, <td>, <tr>), GUIONES ('-') O VIÑETAS.\n"
        "- Todo el documento debe estructurarse en UNA SOLA COLUMNA continua alineada a la izquierda.\n"
        "- NO utilices sintaxis Markdown (sin asteriscos '**', sin almohadillas '#').\n"
        "- Cada sección principal debe abrir con una etiqueta <h3> en MAYÚSCULAS puros (ej: <h3>HABILIDADES TÉCNICAS</h3>).\n"
        "- Para las subcategorías de HABILIDADES TÉCNICAS, IDIOMAS y SOFT SKILLS, escribe cada bloque como un párrafo normal (<p>), "
        "separando los elementos de forma horizontal usando únicamente la barra vertical '|'. "
        "Ejemplo exacto requerido:\n"
        "  <p>Languages: Java | TypeScript | JavaScript | Python</p>\n"
        "  <p>Frameworks: Spring Boot | Angular | React | Node.js | Express.js</p>"
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

