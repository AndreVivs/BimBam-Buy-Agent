"""
Módulo encargado de cargar todos los documentos PDF del proyecto.

Responsabilidades:
- Buscar archivos PDF.
- Cargar su contenido.
- Agregar metadatos personalizados.
- Devolver una lista de documentos de LangChain.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

from app.config import CATEGORY_MAP, DOCUMENTS_PATH
from app.logger import get_logger


logger = get_logger(__name__)


def obtener_categoria(nombre_archivo: str) -> str:
    """
    Obtiene la categoría asociada al nombre base de un PDF.

    Parameters
    ----------
    nombre_archivo:
        Nombre del archivo sin extensión.

        Ejemplo:
        "tiempos y costos de envio"

    Returns
    -------
    str
        Categoría configurada para el documento.

        Ejemplo:
        "envios"

    Raises
    ------
    ValueError
        Si el archivo no está registrado en CATEGORY_MAP.
    """

    nombre_normalizado = nombre_archivo.lower().strip()

    for categoria, nombre_documento in CATEGORY_MAP.items():
        if nombre_documento.lower().strip() == nombre_normalizado:
            return categoria

    raise ValueError(
        f"El documento '{nombre_archivo}' no tiene una categoría "
        "configurada en CATEGORY_MAP."
    )


def cargar_documentos() -> List[Document]:
    """
    Carga todos los archivos PDF ubicados en la carpeta documents.

    Cada página recibe los metadatos personalizados:

    - categoria
    - filename

    Returns
    -------
    List[Document]
        Lista completa de páginas cargadas como documentos de LangChain.

    Raises
    ------
    FileNotFoundError
        Si no existe la carpeta de documentos o no contiene PDFs.

    ValueError
        Si algún PDF no está registrado en CATEGORY_MAP.
    """

    if not DOCUMENTS_PATH.exists():
        raise FileNotFoundError(
            f"No existe la carpeta de documentos: {DOCUMENTS_PATH}"
        )

    if not DOCUMENTS_PATH.is_dir():
        raise NotADirectoryError(
            f"La ruta de documentos no es una carpeta: {DOCUMENTS_PATH}"
        )

    pdfs = sorted(DOCUMENTS_PATH.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(
            f"No se encontraron archivos PDF en: {DOCUMENTS_PATH}"
        )

    logger.info("Se encontraron %s PDFs.", len(pdfs))

    documentos: List[Document] = []

    for archivo in pdfs:
        logger.info("Cargando %s", archivo.name)

        categoria = obtener_categoria(archivo.stem)

        loader = PyMuPDFLoader(str(archivo))
        paginas = loader.load()

        for pagina in paginas:
            pagina.metadata["categoria"] = categoria
            pagina.metadata["filename"] = archivo.name

        documentos.extend(paginas)

        logger.info(
            "%s cargado: %s páginas, categoría=%s",
            archivo.name,
            len(paginas),
            categoria,
        )

    logger.info(
        "Total de páginas cargadas: %s",
        len(documentos),
    )

    return documentos