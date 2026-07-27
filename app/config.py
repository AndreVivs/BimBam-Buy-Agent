"""
config.py
Configuración central del proyecto.
Aquí se definen todas las constantes utilizadas
por el resto de módulos.
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# VARIABLES DE ENTORNO
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
HF_TOKEN: str | None = os.getenv("HF_TOKEN")
OLLAMA_BASE_URL: str = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


# EMBEDDINGS
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# RUTAS
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_PATH = BASE_DIR / "documents"
VECTORSTORE_PATH = BASE_DIR / "vectorstore"
VECTORSTORE_INDEX_NAME = "bimbam_index"

load_dotenv(BASE_DIR / ".env")

# SPLITTER
CHUNK_SIZE = 700
CHUNK_OVERLAP = 150

# RETRIEVER
TOP_K = 6
FETCH_K = 12
LAMBDA_MULT = 0.65
SEARCH_TYPE = "similarity"

# AGENTE
MAX_ITERATIONS = 5
VERBOSE = True


# DICTIONARY DOCUMENTS
CATEGORY_MAP = {
    "envios": "tiempos y costos de envio",
    "garantias": "garantia de productos",
    "pagos": "metodos de pago",
    "afiliados": "programa de afiliados",
    "reembolsos": "reembolsos y devoluciones",
}

# DESCRIPCIONES DE LAS HERRAMIENTAS
TOOL_DESCRIPTIONS = {
    "envios": (
        "Consulta información sobre envíos, tiempos de entrega, "
        "costos de envío, cobertura, transportistas, retrasos "
        "y seguimiento de pedidos."
    ),
    "garantias": (
        "Consulta información sobre garantías de productos, "
        "fallas de fábrica, productos dañados, reparaciones, "
        "cambios, reemplazos y servicio técnico."
    ),
    "pagos": (
        "Consulta información sobre métodos de pago, pagos rechazados, "
        "cobros duplicados, pagos en cuotas, conciliación, "
        "cancelaciones y problemas con transacciones."
    ),
    "afiliados": (
        "Consulta información sobre el programa de afiliados, "
        "comisiones, requisitos, enlaces de afiliación, seguimiento "
        "de ventas y pagos a afiliados."
    ),
    "reembolsos": (
        "Consulta información sobre devoluciones, retracto, "
        "reembolsos, plazos para devolver productos, condiciones "
        "de devolución y estado de solicitudes."
    ),
}

# CONFIGURACIÓN DEL LLM(MODELO DE LENGUAJE)
LLM_MODEL = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.0
LLM_MAX_RETRIES = 2
LLM_TIMEOUT = 60

# CONFIGURACIÓN DEL AGENTE
AGENT_VERBOSE = True #nos permitirá ver qué herramienta selecciona durante las pruebas.
AGENT_MAX_ITERATIONS = 6 #evita ciclos indefinidos
AGENT_HANDLE_PARSING_ERRORS = True
