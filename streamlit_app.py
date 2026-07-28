"""
streamlit_app.py

Interfaz web del asistente virtual de BimBam Buy.
"""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from app.agent import consultar_agente


# ------------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------------

st.set_page_config(
    page_title="BimBam Buy",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------
# Estilos
# ------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 6rem;
        }

        .app-subtitle {
            color: #6b7280;
            margin-top: -12px;
            margin-bottom: 24px;
        }

        .sidebar-note {
            font-size: 0.88rem;
            color: #6b7280;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Estado de sesión
# ------------------------------------------------------------------

MENSAJE_INICIAL = (
    "¡Hola! Soy el asistente virtual de BimBam Buy. "
    "Puedo ayudarte con envíos, pagos, garantías, "
    "reembolsos, devoluciones y el programa de afiliados."
)


def inicializar_estado() -> None:
    """
    Inicializa las variables requeridas por la interfaz.
    """

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": MENSAJE_INICIAL,
                "steps": [],
            }
        ]


def limpiar_conversacion() -> None:
    """
    Elimina el historial de la sesión actual.
    """

    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": MENSAJE_INICIAL,
            "steps": [],
        }
    ]


def construir_chat_history():
    """
    Convierte el historial de Streamlit al formato
    de mensajes esperado por LangChain.

    Se omite el último mensaje porque corresponde a
    la consulta que se enviará como pregunta actual.
    """

    historial = []

    for mensaje in st.session_state.mensajes[:-1]:
        contenido = mensaje["content"]

        if mensaje["role"] == "user":
            historial.append(
                HumanMessage(content=contenido)
            )
        else:
            historial.append(
                AIMessage(content=contenido)
            )

    return historial


# ------------------------------------------------------------------
# Inicialización
# ------------------------------------------------------------------

inicializar_estado()


# ------------------------------------------------------------------
# Barra lateral
# ------------------------------------------------------------------

with st.sidebar:
    st.title("🛍️ BimBam Buy")

    st.markdown(
        """
        Asistente especializado en:

        - 🚚 Envíos
        - 💳 Métodos de pago
        - 🛡️ Garantías
        - ↩️ Reembolsos y devoluciones
        - 🤝 Programa de afiliados
        """
    )

    st.divider()

    if st.button(
        "🗑️ Limpiar conversación",
        use_container_width=True,
    ):
        limpiar_conversacion()
        st.rerun()

    st.markdown(
        """
        <p class="sidebar-note">
        Las respuestas se generan usando las políticas
        internas disponibles de BimBam Buy.
        </p>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------

st.title("Asistente virtual")

st.markdown(
    """
    <p class="app-subtitle">
        ¿En qué podemos ayudarte hoy?
    </p>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Historial visible
# ------------------------------------------------------------------

for mensaje in st.session_state.mensajes:
    role = mensaje["role"]

    avatar = "👤" if role == "user" else "🛍️"

    with st.chat_message(
        role,
        avatar=avatar,
    ):
        st.markdown(mensaje["content"])

        steps = mensaje.get("steps", [])

        if role == "assistant" and steps:
            with st.expander(
                "Información consultada",
                expanded=False,
            ):
                for numero, paso in enumerate(
                    steps,
                    start=1,
                ):
                    herramienta = paso.get(
                        "tool",
                        "consulta interna",
                    )

                    entrada = paso.get(
                        "tool_input",
                        {},
                    )

                    estado = (
                        "Error"
                        if paso.get("error")
                        else "Completado"
                    )

                    st.markdown(
                        f"**{numero}. {herramienta}**"
                    )

                    st.caption(
                        f"Estado: {estado}"
                    )

                    query = entrada.get("query")

                    if query:
                        st.markdown(
                            f"Consulta: `{query}`"
                        )


# ------------------------------------------------------------------
# Entrada del usuario
# ------------------------------------------------------------------

pregunta = st.chat_input(
    "Escribe tu pregunta sobre BimBam Buy...",
    max_chars=2_000,
)


if pregunta:
    pregunta = pregunta.strip()

    if not pregunta:
        st.warning(
            "Escribe una pregunta antes de enviarla."
        )
        st.stop()

    # Guardar y mostrar inmediatamente el mensaje del usuario.
    st.session_state.mensajes.append(
        {
            "role": "user",
            "content": pregunta,
            "steps": [],
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):
        st.markdown(pregunta)

    # Construir historial antes de consultar al agente.
    chat_history = construir_chat_history()

    with st.chat_message(
        "assistant",
        avatar="🛍️",
    ):
        try:
            with st.spinner(
                "Consultando información de BimBam Buy...",
                show_time=True,
            ):
                resultado = consultar_agente(
                    pregunta=pregunta,
                    chat_history=chat_history,
                )

            respuesta = resultado.get(
                "output",
                "",
            ).strip()

            pasos = resultado.get(
                "intermediate_steps",
                [],
            )

            if not respuesta:
                respuesta = (
                    "No pude elaborar una respuesta con "
                    "la información disponible."
                )

            st.markdown(respuesta)

            if pasos:
                with st.expander(
                    "Información consultada",
                    expanded=False,
                ):
                    for numero, paso in enumerate(
                        pasos,
                        start=1,
                    ):
                        herramienta = paso.get(
                            "tool",
                            "consulta interna",
                        )

                        entrada = paso.get(
                            "tool_input",
                            {},
                        )

                        estado = (
                            "Error"
                            if paso.get("error")
                            else "Completado"
                        )

                        st.markdown(
                            f"**{numero}. {herramienta}**"
                        )

                        st.caption(
                            f"Estado: {estado}"
                        )

                        query = entrada.get("query")

                        if query:
                            st.markdown(
                                f"Consulta: `{query}`"
                            )

            st.session_state.mensajes.append(
                {
                    "role": "assistant",
                    "content": respuesta,
                    "steps": pasos,
                }
            )

        except Exception as error:
            mensaje_error = (
                "Ocurrió un problema al procesar tu consulta. "
                "Por favor, inténtalo nuevamente."
            )

            st.error(mensaje_error)

            st.session_state.mensajes.append(
                {
                    "role": "assistant",
                    "content": mensaje_error,
                    "steps": [],
                }
            )

            # Durante desarrollo resulta útil ver el error real.
            with st.expander(
                "Detalle técnico",
                expanded=False,
            ):
                st.exception(error)