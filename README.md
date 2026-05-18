# Mi Chatbot IA

Este proyecto es una aplicación de chat basada en Streamlit que usa la API de Groq para generar respuestas de inteligencia artificial.

## Qué hace

- Proporciona una interfaz de chat profesional y moderna.
- Permite seleccionar el modelo de IA entre varias opciones.
- Ofrece ajuste de tono de respuesta (Formal, Informal, Profesional).
- Mantiene el historial de conversación en la sesión.
- Incluye control para reiniciar el chat y mensajes de estado.

## Dependencias

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
streamlit run ChatBot.py
```

## Modelos compatibles

El proyecto ahora usa modelos más actuales de Groq:

- `gemma-1.5b`
- `gemma2-7b`
- `gemma2-13b`

## Estilo

La aplicación tiene un diseño de interfaz rojo claro con botones más definidos y paneles mejorados.

## Configuración de la API

La clave de API debe configurarse en `.streamlit/secrets.toml` como:

```toml
CLAVE_API = "tu_clave_api"
```

También es posible usar la variable de entorno `GROQ_API_KEY`.

## Pruebas manuales

1. Ejecuta la aplicación.
2. Selecciona un modelo en la barra lateral.
3. Escribe un mensaje en la caja de chat.
4. Observa la respuesta generada y verifica el historial.
5. Usa "Reiniciar conversación" para limpiar el chat.
