
import pdfplumber


def extraer_texto_pdf(archivo_pdf):
    """
    Extrae el texto de todas las páginas de un PDF.
    Admite rutas y archivos subidos mediante Streamlit.
    """

    texto_completo = ""

    try:
        if hasattr(archivo_pdf, "seek"):
            archivo_pdf.seek(0)

        with pdfplumber.open(archivo_pdf) as pdf:

            if not pdf.pages:
                return "Error al leer el archivo PDF: documento vacío."

            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()

                if texto_pagina:
                    texto_completo += texto_pagina + "\n"

        texto_completo = texto_completo.strip()

        if not texto_completo:
            return (
                "Error al leer el archivo PDF: "
                "no se ha podido extraer texto. "
                "Comprueba si es un PDF escaneado o protegido."
            )

        return texto_completo

    except Exception as e:
        return f"Error al leer el archivo PDF: {str(e)}"

    finally:
        if hasattr(archivo_pdf, "seek"):
            archivo_pdf.seek(0)
