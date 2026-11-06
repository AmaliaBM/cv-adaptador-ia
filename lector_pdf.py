import pdfplumber

def extraer_texto_pdf(archivo_pdf):
    """
    Recibe un archivo PDF (ya sea una ruta o un objeto de archivo subido en Streamlit),
    extrae el texto de todas sus páginas y lo devuelve como un único string.
    """
    texto_completo = ""
    
    try:
        # Abrimos el archivo PDF usando pdfplumber
        with pdfplumber.open(archivo_pdf) as pdf:
            # Recorremos cada página del documento
            for pagina in pdf.pages:
                # Extraemos el texto de la página actual
                texto_pagina = pagina.extract_text()
                
                # Si la página contiene texto, lo añadimos al string completo
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
        
        # Eliminamos espacios en blanco innecesarios al inicio y al final
        return texto_completo.strip()
        
    except Exception as e:
        # Si algo falla (por ejemplo, un PDF corrupto o protegido), devolvemos el error
        return f"Error al leer el archivo PDF: {str(e)}"
