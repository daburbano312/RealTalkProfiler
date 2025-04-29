# RealTalk Profiler

**RealTalk Profiler** es una aplicación web en tiempo real diseñada para procesar grabaciones de audio, convertir el habla en texto, analizar la emoción del hablante, extraer palabras clave y generar recomendaciones personalizadas para asesores en ventas inmobiliarias.

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

2. Crea un entorno virtual e instálalo:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/macOS
   venv\Scripts\activate     # En Windows

3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt

4. Crea un archivo .env con las siguientes variables:
   ```bash
   OPENAI_API_KEY=tu-clave-api-de-openai
   FLASK_SECRET_KEY=una-clave-secreta-para-flask

5. Corre la aplicación:
   ```bash
   flask run

La aplicación estará disponible en http://127.0.0.1:5000/.

## Uso

Una vez que la aplicación esté corriendo, puedes acceder a las siguientes rutas:

- /: Página principal donde se inicia la grabación y se ve la transcripción en vivo.

- /proyectos: Ver proyectos inmobiliarios disponibles.

- /historial: Ver el historial de las transcripciones.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.