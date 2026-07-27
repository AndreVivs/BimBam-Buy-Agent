"""
vectorstore.py

Gestiona la creación, persistencia y carga
del índice vectorial FAISS.
"""

from functools import lru_cache

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    VECTORSTORE_INDEX_NAME,
    VECTORSTORE_PATH,
)
from app.loaders import cargar_documentos


@lru_cache(maxsize=1)
def crear_embeddings() -> HuggingFaceEmbeddings:
    """
    Crea y reutiliza el modelo de embeddings durante
    toda la ejecución del programa.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )


def crear_splitter() -> RecursiveCharacterTextSplitter:
    """
    Crea el separador de documentos.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )


def _indice_existe() -> bool:
    """
    Verifica que existan los dos archivos requeridos por FAISS.
    """

    faiss_file = (
        VECTORSTORE_PATH
        / f"{VECTORSTORE_INDEX_NAME}.faiss"
    )

    pkl_file = (
        VECTORSTORE_PATH
        / f"{VECTORSTORE_INDEX_NAME}.pkl"
    )

    return faiss_file.exists() and pkl_file.exists()


def crear_vectorstore(
    documentos: list[Document],
) -> FAISS:
    """
    Divide los documentos, crea el índice FAISS
    y lo guarda localmente.
    """

    if not documentos:
        raise ValueError(
            "No se recibieron documentos para crear el vectorstore."
        )

    splitter = crear_splitter()
    embeddings = crear_embeddings()

    chunks = splitter.split_documents(documentos)

    if not chunks:
        raise ValueError(
            "No se pudieron generar chunks a partir de los documentos."
        )

    print(f"Chunks creados: {len(chunks)}")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    VECTORSTORE_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    vectorstore.save_local(
        folder_path=str(VECTORSTORE_PATH),
        index_name=VECTORSTORE_INDEX_NAME,
    )

    print("FAISS creado correctamente.")

    return vectorstore


def cargar_vectorstore() -> FAISS:
    """
    Carga el índice FAISS almacenado localmente.

    El índice se considera confiable porque fue creado
    localmente por esta misma aplicación.
    """

    embeddings = crear_embeddings()

    vectorstore = FAISS.load_local(
        folder_path=str(VECTORSTORE_PATH),
        embeddings=embeddings,
        index_name=VECTORSTORE_INDEX_NAME,
        allow_dangerous_deserialization=True,
    )

    print("FAISS cargado correctamente.")

    return vectorstore


def obtener_vectorstore() -> FAISS:
    """
    Devuelve un vectorstore listo para usar.

    Si el índice existe, lo carga directamente.
    Si no existe, carga los PDF y crea el índice.
    """

    if _indice_existe():
        return cargar_vectorstore()

    print("No existe un índice FAISS. Creándolo...")

    documentos = cargar_documentos()

    return crear_vectorstore(documentos)