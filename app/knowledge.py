"""
knowledge.py

Ensambla la capa de conocimiento del proyecto.
"""

from langchain_core.vectorstores import VectorStoreRetriever

from app.config import CATEGORY_MAP
from app.retriever import (
    crear_retriever_categoria,
    crear_retriever_general,
)
from app.vectorstore import obtener_vectorstore


def obtener_categorias() -> list[str]:
    """
    Devuelve las categorías configuradas.
    """

    return sorted(CATEGORY_MAP.keys())


def cargar_conocimiento() -> dict[str, VectorStoreRetriever]:
    """
    Construye el retriever general y los retrievers
    especializados por categoría.
    """

    vectorstore = obtener_vectorstore()

    retrievers: dict[str, VectorStoreRetriever] = {
        "general": crear_retriever_general(vectorstore),
    }

    for categoria in obtener_categorias():
        retrievers[categoria] = crear_retriever_categoria(
            vectorstore=vectorstore,
            categoria=categoria,
        )

    return retrievers