import os

import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Mi Chatbot IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

def aplicar_estilos_personalizados():
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #ffe5e5 0%, #ffd6d6 100%) !important;
        }
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 20px;
            padding: 1rem;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .stButton>button {
            background-color: #b91c1c;
            color: white;
            border-radius: 12px;
            border: none;
            padding: 0.8rem 1.2rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #991b1b;
        }
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 1px solid #fca5a5;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #7f1d1d;
        }
        .stChatMessage>div, .streamlit-chat-message-row {
            border-radius: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

MODELOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "groq/compound",
]

EXCLUSIONES_MODELOS = [
    "whisper",
    "prompt-guard",
    "safeguard",
    "audio",
    "translate",
    "speech",
]

DEFAULT_SYSTEM_PROMPT = (
    "Eres un asistente conversacional claro, amable y profesional. "
    "Responde con precisión y ayuda en cada consulta."
)

def configurar_pagina(modelos_disponibles):
    st.sidebar.title("Ajustes del chat")
    st.sidebar.markdown(
        "Seleccioná el modelo y ajustá el comportamiento del asistente para obtener respuestas más alineadas a tu estilo."
    )
    elegir_modelo = st.sidebar.selectbox("Modelo", options=modelos_disponibles, index=0)
    tono = st.sidebar.selectbox(
        "Tono de respuesta",
        options=["Formal", "Informal", "Profesional"],
        index=2,
    )
    mostrar_ayuda = st.sidebar.checkbox("Mostrar guía rápida", value=True)
    return elegir_modelo, tono, mostrar_ayuda


def es_modelo_valido(modelo_id: str) -> bool:
    modelo_id_lower = modelo_id.lower()
    return not any(exclusion in modelo_id_lower for exclusion in EXCLUSIONES_MODELOS)


def obtener_modelos_disponibles(cliente):
    try:
        respuesta = cliente.models.list()
        modelos = [
            item.id
            for item in respuesta.data
            if getattr(item, "active", False) and es_modelo_valido(item.id)
        ]
        if modelos:
            return modelos
    except Exception as error:
        st.warning(
            "No se pudo cargar la lista de modelos desde la API. "
            "Se usarán opciones predeterminadas."
        )
        st.write(f"Detalle: {error}")
    return MODELOS



# Función que conecta con Groq
def crear_usuario_groq():
    clave_secreta = st.secrets.get("CLAVE_API") or os.environ.get("GROQ_API_KEY")
    if not clave_secreta:
        st.error(
            "No se encontró la clave API. Agregala en `.streamlit/secrets.toml` "
            "como `CLAVE_API`, o define la variable de entorno `GROQ_API_KEY`."
        )
        st.stop()
    return Groq(api_key=clave_secreta)

# Configurar el modelo y el mensaje del usuario
def configurar_modelo(cliente, modelo, mensaje_entrada):
    return cliente.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": mensaje_entrada}],
        stream=True
    )

def inicializacion_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "modelo" not in st.session_state:
        st.session_state.modelo = MODELOS[0]

# Actualizar historial 
def actualizar_historial(rol, contenido, avatar):
    st.session_state.mensajes.append({"role": rol, "content": contenido, "avatar": avatar})

# Mostrar historial 
def mostrar_historial():
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.markdown(mensaje["content"])

# Área del chat
def area_chat():
    st.markdown("### Conversación")
    if not st.session_state.mensajes:
        st.info("Escribí tu primer mensaje y el asistente responderá en esta ventana.")
        return
    mostrar_historial()

# Generar respuesta desde la API
def generar_respuesta(chat_completo):
    respuesta_completa = ""
    for frase in chat_completo:
        if frase.choices[0].delta.content:
            contenido = frase.choices[0].delta.content
            respuesta_completa += contenido
            yield contenido
    return respuesta_completa

def main():
    aplicar_estilos_personalizados()
    st.markdown("# Chat-bot IA")
    st.markdown("### Asistente inteligente")
    st.markdown(
        "Bienvenido. Elegí un modelo y enviá tu mensaje para obtener respuestas claras, útiles y rápidas."
    )
    cliente_usuario = crear_usuario_groq()
    modelos_disponibles = st.session_state.get("modelos_disponibles")
    if not modelos_disponibles:
        modelos_disponibles = obtener_modelos_disponibles(cliente_usuario)
        st.session_state.modelos_disponibles = modelos_disponibles
    modelo, tono, mostrar_ayuda = configurar_pagina(modelos_disponibles)
    inicializacion_estado()
    st.session_state.modelo = modelo
    if mostrar_ayuda:
        st.info(
            "Usa el campo de chat al final de la página para enviar mensajes. "
            "Elegí un modelo en la barra lateral y ajusta el tono de la respuesta."
        )

    columnas = st.columns([3, 1])
    with columnas[0]:
        st.markdown("## Chat en vivo")
        area_chat()
        mensaje = st.chat_input("Escribí tu mensaje aquí...")
        if mensaje:
            actualizar_historial("user", mensaje, "👤")
            prompt = f"Tono: {tono}. {st.session_state.system_prompt}\nUsuario: {mensaje}"
            try:
                chat_completo = configurar_modelo(cliente_usuario, modelo, prompt)
                with st.chat_message("assistant", avatar="🤖"):
                    respuesta_completa = st.write_stream(generar_respuesta(chat_completo))
                actualizar_historial("assistant", respuesta_completa, "🤖")
            except Exception as error:
                st.error(f"Error de conexión con la API: {error}")
    with columnas[1]:
        st.markdown("## Panel de control")
        st.info("Monitorea el modelo, el tono y controla la conversación desde aquí.")
        st.markdown("### Ajustes activos")
        st.write(f"**Modelo activo:** {modelo}")
        st.write(f"**Tono seleccionado:** {tono}")
        if st.button("Reiniciar conversación"):
            st.session_state.mensajes = []
            st.success("Historial borrado. Podés empezar una nueva conversación.")
        st.markdown("---")
        st.markdown("#### Ideas para probar")
        st.markdown(
            "- Preguntale sobre ideas, dudas técnicas o contenido creativo.\n"
            "- Cambiá el tono para variar la formalidad.\n"
            "- Reiniciá la conversación si querés empezar desde cero."
        )

if __name__ == "__main__":
    main()

