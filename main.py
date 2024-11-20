import streamlit as st
from groq import Groq

# Crear usuario Groq
def crear_usuario_groq():
    clave_secreta = st.secrets["CLAVE_API"]
    return Groq(api_key=clave_secreta)

# Configuración de la página
st.set_page_config(page_title="Mi chat de IA", page_icon="🤖", layout="centered")

MODELOS = ['llama3-8b-8192', 'llama3-70b-8192', 'mixtral-8x7b-32768']

def configurar_pagina():
    st.title("🤖 Tu bot para charlar")
    st.text("⚠️ Hazme preguntas y toca el botón 'Finalizar conversación' para guardar nuestra charla (tenes hasta 5 para guardar) si reinicias la pagina se pierde todo. ⚠️")
    st.sidebar.title("Configuración y historial")
    st.sidebar.write("Puedes elegir cualquier modelo dependiendo el modelo la respuesta puede ser mas largo o mas complejo.")
    elegir_modelo = st.sidebar.selectbox('Elige un modelo', options=MODELOS, index=0)
    return elegir_modelo

modelo = configurar_pagina()

# Configurar modelo y generar respuesta
def configurar_modelo(cliente, modelo, mensaje_de_entrada):
    respuesta = cliente.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": mensaje_de_entrada}],
        stream=False
    )
    try:
        return respuesta.choices[0].message.content
    except Exception as e:
        st.error(f"Error al procesar la respuesta: {e}")
        return "Hubo un problema al generar la respuesta."

# Inicializar el estado de la aplicación
def inicializar_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "conversaciones" not in st.session_state:
        st.session_state.conversaciones = []

# Guardar la conversación actual en el historial
def guardar_conversacion():
    if st.session_state.mensajes:
        st.session_state.conversaciones.append(st.session_state.mensajes.copy())  # Usar copia para evitar referencias
        # Mantener solo las últimas 5 conversaciones
        if len(st.session_state.conversaciones) > 5:
            st.session_state.conversaciones.pop(0)
        # Reiniciar mensajes para una nueva conversación
        st.session_state.mensajes = []
        return True
    return False

# Mostrar historial de mensajes (última conversación)
def mostrar_historial():
    st.subheader("Historial de la conversación actual")
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.markdown(mensaje["content"])

# Mostrar historial de todas las conversaciones (últimas 5)
def mostrar_conversaciones():
    st.sidebar.subheader("Últimas 5 conversaciones")
    for i, conversacion in enumerate(st.session_state.conversaciones):
        with st.sidebar.expander(f"Conversación {i + 1}"):
            for mensaje in conversacion:
                if mensaje["role"] == "user":
                    st.write(f"**Tú:** {mensaje['content']}")
                else:
                    st.write(f"**Asistente:** {mensaje['content']}")

# Inicializar cliente y estado
cliente_usuario = crear_usuario_groq()
inicializar_estado()

# Mostrar historial previo de conversaciones
mostrar_conversaciones()

# Entrada de texto del usuario
mensaje = st.chat_input("Escribe tu mensaje:")

# Si hay un mensaje, procesarlo
if mensaje:
    # Agregar mensaje del usuario al historial
    st.session_state.mensajes.append({"role": "user", "content": mensaje, "avatar": "🧑‍💻"})
    
    # Obtener respuesta del modelo
    respuesta_chatbot = configurar_modelo(cliente_usuario, modelo, mensaje)
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_chatbot, "avatar": "🤖"})

# Mostrar historial actualizado si hay mensajes
if st.session_state.mensajes:
    mostrar_historial()

# Botón para finalizar la conversación (aparece solo si hay mensajes)
if st.session_state.mensajes:
    if st.button("Finalizar conversación"):
        if guardar_conversacion():
            st.success("Conversación guardada exitosamente.")
            # Mostrar historial vacío y actualizar la barra lateral inmediatamente
            st.rerun()

