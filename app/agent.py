"""
agent.py

Orquesta el uso de herramientas de recuperación mediante
tool calling nativo.

El flujo tiene un máximo de una ronda de recuperación:

1. El LLM analiza la consulta.
2. Selecciona una o varias herramientas.
3. Las herramientas se ejecutan una sola vez.
4. El LLM redacta la respuesta final sin volver a llamar herramientas.
"""

from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool

from app.knowledge import cargar_conocimiento
from app.llm import crear_llm
from app.prompts import SYSTEM_PROMPT
from app.tools import crear_tools

from app.prompts import (
    FINAL_RESPONSE_PROMPT,
    SYSTEM_PROMPT,
)


@lru_cache(maxsize=1)
def obtener_componentes_agente() -> tuple[
    BaseChatModel,
    list[BaseTool],
    dict[str, BaseTool],
]:
    """
    Construye y reutiliza el LLM y las herramientas.

    Returns:
        Tupla con:
        - LLM base.
        - Lista de herramientas.
        - Diccionario de herramientas por nombre.
    """

    retrievers = cargar_conocimiento()
    tools = crear_tools(retrievers)
    llm = crear_llm()

    tools_por_nombre = {
        tool.name: tool
        for tool in tools
    }

    if len(tools_por_nombre) != len(tools):
        raise ValueError(
            "Existen herramientas con nombres duplicados."
        )

    return llm, tools, tools_por_nombre


def construir_mensajes_iniciales(
    pregunta: str,
    chat_history: list[BaseMessage] | None = None,
) -> list[BaseMessage]:
    """
    Construye los mensajes enviados al modelo para seleccionar
    las herramientas.
    """

    pregunta_limpia = pregunta.strip()

    if not pregunta_limpia:
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    mensajes: list[BaseMessage] = [
        SystemMessage(content=SYSTEM_PROMPT),
    ]

    if chat_history:
        mensajes.extend(chat_history)

    mensajes.append(
        HumanMessage(content=pregunta_limpia)
    )

    return mensajes


def normalizar_argumentos_tool(
    argumentos: Any,
    pregunta_original: str,
) -> dict[str, Any]:
    """
    Normaliza los argumentos generados por el modelo.

    Las herramientas retriever esperan un argumento llamado
    'query'. Si el modelo devuelve un texto directamente, se
    convierte al formato esperado.

    No se permite ejecutar una herramienta con una consulta vacía.
    """

    if isinstance(argumentos, str):
        query = argumentos.strip()

        if not query:
            query = pregunta_original

        return {
            "query": query,
        }

    if not isinstance(argumentos, dict):
        return {
            "query": pregunta_original,
        }

    query = argumentos.get("query")

    if not isinstance(query, str) or not query.strip():
        argumentos["query"] = pregunta_original
    else:
        argumentos["query"] = query.strip()

    return argumentos


def ejecutar_tool_calls(
    tool_calls: list[dict[str, Any]],
    tools_por_nombre: dict[str, BaseTool],
    pregunta_original: str,
) -> tuple[list[ToolMessage], list[dict[str, Any]]]:
    """
    Ejecuta todas las herramientas solicitadas por el modelo
    exactamente una vez.

    Returns:
        - Mensajes ToolMessage para la síntesis final.
        - Registro legible de las herramientas utilizadas.
    """

    mensajes_herramientas: list[ToolMessage] = []
    pasos: list[dict[str, Any]] = []

    herramientas_ejecutadas: set[
        tuple[str, str]
    ] = set()

    for tool_call in tool_calls:
        nombre = tool_call.get("name")
        tool_call_id = tool_call.get("id")
        argumentos_originales = tool_call.get("args", {})

        if not nombre:
            continue

        if nombre not in tools_por_nombre:
            resultado = (
                f"No existe una herramienta registrada "
                f"con el nombre '{nombre}'."
            )

            mensajes_herramientas.append(
                ToolMessage(
                    content=resultado,
                    tool_call_id=tool_call_id or nombre,
                    name=nombre,
                )
            )

            pasos.append(
                {
                    "tool": nombre,
                    "tool_input": argumentos_originales,
                    "output": resultado,
                    "error": True,
                }
            )

            continue

        argumentos = normalizar_argumentos_tool(
            argumentos=argumentos_originales,
            pregunta_original=pregunta_original,
        )

        clave_ejecucion = (
            nombre,
            str(argumentos),
        )

        if clave_ejecucion in herramientas_ejecutadas:
            continue

        herramientas_ejecutadas.add(clave_ejecucion)

        tool = tools_por_nombre[nombre]

        try:
            resultado = tool.invoke(argumentos)
            resultado_texto = str(resultado)
            hubo_error = False

        except Exception as error:
            resultado_texto = (
                "No fue posible consultar esta categoría. "
                f"Detalle interno: {error}"
            )
            hubo_error = True

        mensajes_herramientas.append(
            ToolMessage(
                content=resultado_texto,
                tool_call_id=tool_call_id or nombre,
                name=nombre,
            )
        )

        pasos.append(
            {
                "tool": nombre,
                "tool_input": argumentos,
                "output": resultado_texto,
                "error": hubo_error,
            }
        )

    return mensajes_herramientas, pasos


def obtener_texto_respuesta(
    mensaje: AIMessage,
) -> str:
    """
    Obtiene de forma segura el contenido textual de un AIMessage.
    """

    contenido = mensaje.content

    if isinstance(contenido, str):
        return contenido.strip()

    return str(contenido).strip()


def consultar_agente(
    pregunta: str,
    chat_history: list[BaseMessage] | None = None,
) -> dict[str, Any]:
    """
    Atiende una consulta utilizando tool calling nativo.

    El modelo puede seleccionar varias herramientas, pero solo
    existe una ronda de recuperación. La respuesta final se genera
    con el LLM sin herramientas vinculadas, evitando bucles.

    Returns:
        Diccionario con:
        - output: respuesta final.
        - intermediate_steps: herramientas ejecutadas.
        - tool_calls: llamadas originales solicitadas por el LLM.
    """

    pregunta_limpia = pregunta.strip()

    if not pregunta_limpia:
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    llm, tools, tools_por_nombre = (
        obtener_componentes_agente()
    )

    mensajes = construir_mensajes_iniciales(
        pregunta=pregunta_limpia,
        chat_history=chat_history,
    )

    # Primera llamada:
    # el modelo decide qué herramientas necesita.
    llm_con_tools = llm.bind_tools(
        tools,
        tool_choice="auto",
    )

    decision = llm_con_tools.invoke(mensajes)

    if not isinstance(decision, AIMessage):
        raise TypeError(
            "El modelo no devolvió un AIMessage válido."
        )

    tool_calls = decision.tool_calls or []

    # Consulta fuera del ámbito de BimBam Buy o respuesta
    # que no requiere recuperar políticas internas.
    if not tool_calls:
        respuesta_directa = obtener_texto_respuesta(
            decision
        )

        if not respuesta_directa:
            respuesta_directa = (
                "Solo puedo ayudarte con consultas relacionadas "
                "con BimBam Buy."
            )

        return {
            "output": respuesta_directa,
            "intermediate_steps": [],
            "tool_calls": [],
        }

    mensajes_tools, pasos = ejecutar_tool_calls(
        tool_calls=tool_calls,
        tools_por_nombre=tools_por_nombre,
        pregunta_original=pregunta_limpia,
    )

    if not mensajes_tools:
        return {
            "output": (
                "No pude consultar la información necesaria "
                "para responder tu solicitud."
            ),
            "intermediate_steps": pasos,
            "tool_calls": tool_calls,
        }

    # Segunda y última llamada:
    # se usa el LLM base, sin herramientas vinculadas.
    # Por eso no puede volver a ejecutar un retriever.
    mensajes_finales: list[BaseMessage] = [
        SystemMessage(
            content=(
                SYSTEM_PROMPT
                + "\n\n"
                + FINAL_RESPONSE_PROMPT
            )
        ),
    ]

    if chat_history:
        mensajes_finales.extend(chat_history)

    mensajes_finales.extend(
        [
            HumanMessage(content=pregunta_limpia),
            decision,
            *mensajes_tools,
        ]
    )

    respuesta_final = llm.invoke(
        mensajes_finales
    )

    if not isinstance(respuesta_final, AIMessage):
        raise TypeError(
            "El modelo no devolvió una respuesta final válida."
        )

    output = obtener_texto_respuesta(
        respuesta_final
    )

    if not output:
        output = (
            "No pude elaborar una respuesta con la "
            "información disponible."
        )

    return {
        "output": output,
        "intermediate_steps": pasos,
        "tool_calls": tool_calls,
    }