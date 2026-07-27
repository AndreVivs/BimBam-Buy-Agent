"""
retriever.py

Configura los retrievers utilizados para consultar
el índice vectorial FAISS.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever

from app.config import (
    FETCH_K,
    LAMBDA_MULT,
    SEARCH_TYPE,
    TOP_K,
)


def crear_retriever_general(
    vectorstore: FAISS,
) -> VectorStoreRetriever:
    """
    Crea un retriever que busca en toda la documentación.

    Parameters
    ----------
    vectorstore:
        Índice FAISS que contiene los documentos.

    Returns
    -------
    VectorStoreRetriever
        Retriever configurado con búsqueda MMR.
    """

    return vectorstore.as_retriever(
        search_type=SEARCH_TYPE,
        search_kwargs={
            "k": TOP_K,
            "fetch_k": FETCH_K,
            "lambda_mult": LAMBDA_MULT,
        },
    )


def crear_retriever_categoria(
    vectorstore: FAISS,
    categoria: str,
) -> VectorStoreRetriever:
    """
    Crea un retriever limitado a una categoría documental.

    Parameters
    ----------
    vectorstore:
        Índice FAISS que contiene los documentos.

    categoria:
        Categoría guardada en los metadatos de los chunks,
        por ejemplo: pagos, envios o garantias.

    Returns
    -------
    VectorStoreRetriever
        Retriever filtrado por categoría.
    """

    if not categoria.strip():
        raise ValueError("La categoría no puede estar vacía.")

    return vectorstore.as_retriever(
        search_type=SEARCH_TYPE,
        search_kwargs={
            "k": TOP_K,
            "fetch_k": FETCH_K,
            "lambda_mult": LAMBDA_MULT,
            "filter": {
                "categoria": categoria,
            },
        },
    )