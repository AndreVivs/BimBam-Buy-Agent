"""
llm.py

Configura y crea el modelo de lenguaje utilizado
por el agente de BimBam Buy.
"""

from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import (
    GROQ_API_KEY,
    LLM_MAX_RETRIES,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
)


def validar_configuracion_llm() -> None:
    """
    Valida que exista la configuración necesaria
    para conectarse con Groq.

    Raises
    ------
    ValueError
        Si GROQ_API_KEY no está configurada.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "No se encontró GROQ_API_KEY. "
            "Agrégala al archivo .env del proyecto."
        )

    if not GROQ_API_KEY.strip():
        raise ValueError(
            "GROQ_API_KEY está vacía. "
            "Verifica el archivo .env del proyecto."
        )


@lru_cache(maxsize=1)
def crear_llm() -> ChatGroq:
    """
    Crea y reutiliza el modelo de lenguaje de Groq.
    """

    validar_configuracion_llm()

    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_retries=LLM_MAX_RETRIES,
        timeout=LLM_TIMEOUT,
        disable_streaming="tool_calling",
    )