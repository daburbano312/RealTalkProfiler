# RealTalk Profiler

**RealTalk Profiler** es una aplicación web en tiempo real que procesa grabaciones de audio, convierte el habla a texto, analiza la emoción del hablante, extrae palabras clave y genera recomendaciones personalizadas para ayudar a los asesores en ventas inmobiliarias. Está construida con Flask, Socket.IO, y utiliza inteligencia artificial para análisis de emociones y recomendaciones.

## Funcionalidades

- **Transcripción en vivo**: Convierte el audio grabado a texto en tiempo real.
- **Análisis emocional**: Detecta la emoción predominante en el texto transcrito (por ejemplo, felicidad, tristeza, ira).
- **Extracción de palabras clave**: Identifica las palabras clave más relevantes en el texto transcrito.
- **Generación de recomendaciones**: Basado en la emoción y las palabras clave, genera recomendaciones personalizadas para asesores de ventas inmobiliarias.
- **Interfaz web interactiva**: Permite al usuario iniciar y detener grabaciones, y ver la transcripción, emoción, palabras clave y sugerencias en tiempo real.

## Tecnologías utilizadas

- **Flask**: Framework web para el backend.
- **Flask-SocketIO**: Comunicación en tiempo real a través de WebSockets.
- **Vosk**: Biblioteca de reconocimiento de voz para convertir audio a texto.
- **pyaudio**: Para capturar audio desde el micrófono.
- **OpenAI GPT-4**: Para generar recomendaciones basadas en el análisis de texto.
- **Pysentimiento**: Analiza la emoción en el texto transcrito.
- **SQLite**: Base de datos para almacenar proyectos inmobiliarios.
- **Python-dotenv**: Para gestionar las variables de entorno.

## Instalación

### Requisitos previos

- Python 3.7 o superior
- Acceso a la API de OpenAI (requiere clave de API)

### Pasos para instalar el proyecto

1. Clona este repositorio en tu máquina local:
   ```bash
   git clone <URL del repositorio>
   cd RealTalk-Profiler
