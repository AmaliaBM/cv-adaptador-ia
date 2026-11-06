import os
from groq import Groq

def adaptar_cv_con_ia(texto_cv, texto_oferta, api_key):
    """
    Se conecta a la API de Groq usando el modelo robusto GPT-OSS-120B.
    Adapta el CV a la oferta laboral y resalta los cambios con estilo
    de rotulador fosforito para el frontend.
    """
    client = Groq(api_key=api_key)
    
    prompt_sistema = (
        "Eres un consultor experto en empleabilidad y marca profesional. Tu único objetivo es reescribir y adaptar "
        "el currículum del usuario para que encaje perfectamente con una oferta de empleo específica, "
        "optimizándolo tanto para los algoritmos ATS como para el reclutador humano.\n\n"
        
        "Sigue estas reglas y restricciones técnicas con máxima precisión:\n"
        "1. IDIOMA EXACTO DE LA OFERTA: Identifica las palabras clave esenciales, habilidades técnicas (Hard Skills) "
        "y habilidades blandas (Soft Skills) de la oferta de empleo. Asegúrate de incluir esos términos exactos en el CV "
        "siempre que el usuario tenga experiencia real relacionada.\n"
        "2. REESCRITURA ESTRATÉGICA (MÉTODO STAR): Transforma las descripciones de los puestos de trabajo anteriores del usuario. "
        "En lugar de solo listar tareas comunes, reformúlalas como logros orientados a resultados utilizando verbos de acción fuertes "
        "(ej. 'Lideré', 'Optimicé', 'Desarrollé').\n"
        "3. PERFIL PROFESIONAL DE IMPACTO: Reescribe el resumen inicial (Extracto) para que sea un gancho directo que responda "
        "a la necesidad principal descrita en la oferta de empleo.\n"
        "4. HONESTIDAD TOTAL: Está terminantemente prohibido inventar empresas, títulos universitarios, años de experiencia o tecnologías "
        "que el usuario no haya mencionado en su CV original. La optimización consiste en cambiar la forma de explicar lo que YA sabe hacer.\n"
        "5. OBLIGATORIO - RESALTADO DE CAMBIOS CON ROTULADOR: Cada frase, término clave, métrica, logro o párrafo completo "
        "que hayas modificado, adaptado o añadido con respecto al CV original del usuario DEBES envolverlo estrictamente "
        "entre las etiquetas HTML exactas: <span style='background-color: #fff3cd; color: #856404; padding: 2px 4px; border-radius: 4px; font-weight: 500;'> y </span>. "
        "Lo que no haya sufrido ninguna modificación debe permanecer como texto normal. No olvides cerrar ninguna etiqueta </span>.\n"
        "6. FORMATO: Estructura todo el currículum devuelto usando saltos de línea claros y etiquetas HTML estructurales (como <h3> para títulos "
        "de sección o viñetas simples) para garantizar una visualización web limpia e impecable."
    )
    
    contenido_usuario = f"""
    OFERTA DE EMPLEO:
    {texto_oferta}
    
    --------------------------------------
    CURRÍCULUM ACTUAL DEL USUARIO:
    {texto_cv}
    """
    
    # Realizamos la llamada al modelo robusto de alto rendimiento
    completation = client.chat.completions.create(
        model="openai/gpt-oss-120b", 
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": contenido_usuario}
        ],
        temperature=0.3, 
        max_tokens=2500  # Token máximo aumentado para evitar cortes abruptos y procesar el CV completo
    )
    
    respuesta = completation.choices[0].message.content
    return respuesta if respuesta else ""
