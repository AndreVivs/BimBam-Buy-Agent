"""
tools.py

Crea las herramientas que utilizará el agente
para consultar la base de conocimiento.

Cada categoría documental genera automáticamente
una herramienta especializada.
"""

from langchain_core.tools import BaseTool
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.tools.retriever import create_retriever_tool

from app.config import TOOL_DESCRIPTIONS


def crear_nombre_herramienta(categoria: str) -> str:
    """
    Crea un nombre válido para una herramienta.

    Parameters
    ----------
    categoria:
        Categoría documental, por ejemplo "garantias".

    Returns
    -------
    str
        Nombre de herramienta, por ejemplo "buscar_garantias".
    """

    categoria_normalizada = (
        categoria
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )

    return f"buscar_{categoria_normalizada}"


def crear_tools(
    retrievers: dict[str, VectorStoreRetriever],
) -> list[BaseTool]:
    """
    Crea una herramienta por cada retriever especializado.

    El retriever general no se convierte en herramienta porque
    podría competir con las herramientas específicas y dificultar
    la selección del agente.

    Parameters
    ----------
    retrievers:
        Diccionario generado por cargar_conocimiento().

        Ejemplo:
        {
            "general": retriever,
            "envios": retriever,
            "garantias": retriever,
        }

    Returns
    -------
    list[BaseTool]
        Lista de herramientas disponibles para el agente.

    Raises
    ------
    ValueError
        Si no se reciben retrievers o falta una descripción.
    """

    if not retrievers:
        raise ValueError(
            "No se recibieron retrievers para crear las herramientas."
        )

    tools: list[BaseTool] = []

    for categoria, retriever in retrievers.items():

        if categoria == "general":
            continue

        descripcion = TOOL_DESCRIPTIONS.get(categoria)

        if descripcion is None:
            raise ValueError(
                f"No existe una descripción para la categoría "
                f"'{categoria}' en TOOL_DESCRIPTIONS."
            )
            
        descripcion_tool = (
            f"{descripcion} "
            "Para usar esta herramienta debes enviar obligatoriamente "
            "un argumento llamado 'query' con una consulta de búsqueda "
            "clara y no vacía. "
            "Formato requerido: {'query': 'consulta del cliente'}."
        )

        tool = create_retriever_tool(
            retriever=retriever,
            name=crear_nombre_herramienta(categoria),
            description=descripcion_tool,
        )

        tools.append(tool)
    
    nombres = [tool.name for tool in tools]

    if len(nombres) != len(set(nombres)):
        raise ValueError(
            "Se generaron nombres de herramientas duplicados."
        )

    return tools