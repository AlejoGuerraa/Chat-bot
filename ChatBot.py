import streamlit as st
from groq import Groq

st.set_page_config(page_title="Mi chat de IA", page_icon="🐱‍👤", layout="centered")

st.title("Mi primer chatbot")

nombre = st.text_input("¿Cuál es tu nombre?: ")

if st.button("Saludar"):
    st.write(f"¡Hola {nombre}! Bienvenido/a a mi chatbot, pasala bien.")

modelos = ['llama3-8b-8192', 'llama3-70b-8192', 'gemma2-9b-it']

def configurar_pagina():
    st.title("Chat")
    st.sidebar.title("Configurar la IA")
    elegir_modelo = st.sidebar.selectbox("Elegí un modelo", options=modelos, index=0)
    return elegir_modelo



# Función que conecta con Groq
def crear_usuario_groq():
    clave_secreta = st.secrets["CLAVE_API"]
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
    contenedor_chat = st.container(height=300, border=True)
    with contenedor_chat:
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
    modelo = configurar_pagina()
    cliente_usuario = crear_usuario_groq()
    inicializacion_estado()
    area_chat()

    mensaje = st.chat_input("Escribí algun mensaje")
    if mensaje:
        actualizar_historial("user", mensaje, "👽")
        chat_completo = configurar_modelo(cliente_usuario, modelo, mensaje)
        if chat_completo:
            with st.chat_message("assistant"):
                respuesta_completa = st.write_stream(generar_respuesta(chat_completo))
                actualizar_historial("assistant", respuesta_completa, "🤖")

if __name__ == "__main__":
    main()

