# 💼 Adaptador Estratégico de CV con IA

Un producto de software de código abierto desarrollado en **Python** diseñado con un propósito social: apoyar a personas en situación de desempleo. La aplicación analiza los requisitos técnicos de una oferta de trabajo concreta y reescribe de forma óptima el perfil y la experiencia del usuario. 

El sistema está diseñado bajo un criterio estricto de **optimización dual**: formatea el contenido para superar con éxito las cribas automatizadas de los sistemas **ATS (Applicant Tracking Systems)** y, simultáneamente, aplica metodologías de reclutamiento (como el método **STAR**) para persuadir al reclutador humano, manteniendo siempre la honestidad de los datos originales del candidato.

---

## 🏗️ Arquitectura del Sistema y Flujo de Datos

La aplicación se ha estructurado de forma modular para garantizar un procesamiento ágil y volátil de la información:

1.  **Capa de Interfaz (Frontend):** Construida íntegramente con **Streamlit**. Gestiona el estado de la sesión, la captura de archivos en memoria y la renderización en tiempo real de los datos procesados.
2.  **Motor de Extracción de Datos:** Utiliza la librería **pdfplumber** para abrir los archivos PDF de los usuarios en búferes de memoria. Extrae el texto plano estructurado eliminando elementos visuales complejos (tablas anidadas, imágenes, gráficos de barras de habilidades) que suelen corromper las lecturas de los sistemas ATS corporativos.
3.  **Core de Inferencia (IA):** Conexión mediante SDK privado hacia la API de **Groq Cloud**. Las peticiones se procesan a través del modelo de producción de alta capacidad **`openai/gpt-oss-120b`**, seleccionado por su amplia ventana de contexto y su baja latencia en procesamiento de lenguaje natural en español.

---

## 🎨 Decisiones de Diseño y Experiencia de Usuario (UX/UI)

*   **Auditoría Visual de Cambios:** En lugar de devolver un bloque de texto plano opaco, la interfaz web renderiza un componente HTML dinámico. El motor de IA inyecta etiquetas estáticas en las modificaciones, de modo que **el frontend resalta en amarillo pastel las optimizaciones y palabras clave añadidas**, permitiendo al usuario validar la estrategia de la IA instantáneamente.
*   **Aislamiento de Formatos:** Para proteger la compatibilidad del documento con los algoritmos de selección de las empresas, el sistema separa la vista web del archivo de descarga. Mediante expresiones regulares (`regex`), el backend sanitiza el texto antes de empaquetarlo, ofreciendo un botón de descarga que genera un archivo **Texto Plano (.txt) puro**, garantizando un 100% de éxito en la lectura del ATS.
*   **Estrategia Híbrida de Consumo (BYOK):** Para resolver la escalabilidad financiera del proyecto, se diseñó la lógica *Bring Your Own Key*. La aplicación consume los recursos de la administradora para una primera interacción de cortesía. Si el usuario requiere iterar más veces, la interfaz bloquea el fondo común y activa dinámicamente un campo cifrado para que el usuario introduzca su propia clave de Groq, permitiéndole un uso ilimitado y autónomo sin costes de infraestructura para la plataforma.

---

## 🛡️ Ingeniería de Seguridad y Blindaje de Infraestructura

Al ser un servicio expuesto a internet de forma pública y anónima, se han implementado múltiples capas de seguridad nativas en Python:

*   **Filtro Perimetral Anti-Bots (Gatekeeper):** El acceso a la aplicación está protegido por una pantalla de bienvenida que actúa como un firewall lógico. Obliga a resolver un desafío matemático aleatorio que **expira automáticamente cada 30 segundos** mediante marcas de tiempo (`time.time()`). Esto rompe por completo la automatización de scripts maliciosos de inyección de datos y ataques de fuerza bruta.
*   **Persistencia sin Base de Datos (Anti-F5):** Para evitar el abuso informático de usuarios que intenten consumir los tokens de la administradora refrescando el navegador de forma repetida, se integró un controlador de cookies. Al realizar el primer procesamiento, el backend escribe una cookie persistente en el cliente (`cv_usos_gratuitos`). Al reiniciar la pestaña, el sistema lee el almacenamiento local y mantiene el bloqueo de cortesía.
*   **Privacidad Volátil Radical:** Cumpliendo con los criterios más estrictos de protección de datos, la aplicación no cuenta con capas de persistencia en disco ni bases de datos relacionales. Toda la información (PDFs y ofertas) reside exclusivamente en la memoria RAM del servidor durante el ciclo de vida de la petición HTTP y se destruye por completo al cerrar la conexión.

---

*Proyecto diseñado con arquitectura limpia, enfoque en ciberseguridad y optimización de flujos de trabajo orientados a la empleabilidad.*
