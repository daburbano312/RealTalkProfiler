from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread
import os
import sqlite3
from flask_cors import CORS

from core.use_cases.transcribe_stream import TranscriptionUseCase
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from interfaces.audio.audio_streamer import AudioStreamer
from infrastructure.emotion.text_emotion_detector import TextEmotionAnalyzer
from infrastructure.emotion.keyword_extractor import KeywordExtractor
from infrastructure.ai.openai_recommendation_engine import OpenAIRecommendationEngine  # ✅ NUEVO
from dotenv import load_dotenv
load_dotenv()

# 🧠 Módulos de análisis
text_emotion_analyzer = TextEmotionAnalyzer()
keyword_extractor = KeywordExtractor()
openai_api_key = os.getenv("OPENAI_API_KEY")  # Asegúrate de definir esta variable de entorno

if not openai_api_key:
    raise ValueError("❌ No se encontró la variable de entorno OPENAI_API_KEY. Verifica tu archivo .env o el entorno.")

recommendation_engine = OpenAIRecommendationEngine(api_key=openai_api_key)

emotion_word_buffer = []
MAX_EMOTION_WORDS = 15

# 🔧 Configuración de Flask
app = Flask(__name__,
            template_folder="presentation/web/templates",
            static_folder="presentation/web/static")
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# 🔤 Transcripción
speech_to_text = VoskSpeechToText()
transcriber = TranscriptionUseCase(speech_to_text)

# Variable global para el hilo de grabación
recording_thread = None
recording_active = False  # Bandera para controlar si se está grabando

# 📞 Procesamiento de audio
def handle_audio(audio_chunk):
    global emotion_word_buffer, recording_active

    if not recording_active:
        # Si la grabación fue detenida, ignoramos el procesamiento
        return

    if speech_to_text.accept_waveform(audio_chunk):
        result = speech_to_text.get_result()
        text = result.get("text", "").strip()

        if text:
            print(f"✅ Texto final: {text}")
            socketio.emit("transcription", text)

            # 🧠 Acumulamos palabras para análisis emocional (sin afectar transcripción)
            words = text.split()
            emotion_word_buffer += words
            print(f"🧠 Palabras acumuladas: {len(emotion_word_buffer)}")

            if len(emotion_word_buffer) >= MAX_EMOTION_WORDS:
                full_text = " ".join(emotion_word_buffer[:MAX_EMOTION_WORDS])

                # 🎭 Emoción
                emotion_result = text_emotion_analyzer.analyze(full_text)
                print(f"🎭 Emoción detectada: {emotion_result['emotion']}")
                socketio.emit("emotion", emotion_result)

                # 🔑 Palabras clave
                keywords = keyword_extractor.extract_keywords(full_text)
                print(f"🔑 Palabras clave: {keywords}")
                socketio.emit("keywords", {"keywords": keywords})

                # 📢 Generar sugerencia
                suggestion = recommendation_engine.generate_advice(
                    emotion_result['emotion'],
                    keywords,
                    full_text
                )
                print(f"📢 Sugerencia generada: {suggestion}")
                socketio.emit("suggestion", {"text": suggestion})

                # 🧹 Limpiar buffer
                emotion_word_buffer = emotion_word_buffer[MAX_EMOTION_WORDS:]

# 🎙️ Iniciar el streaming de audio
streamer = AudioStreamer(handle_audio)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def connect():
    print("✅ Cliente conectado vía WebSocket")

# Ruta para la página de proyectos
@app.route("/proyectos")
def proyectos():
    return render_template("projects.html")

# Ruta para obtener los proyectos desde la base de datos
@app.route("/api/proyectos", methods=['GET'])
def obtener_proyectos():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()

        # Obtener los proyectos desde la base de datos
        c.execute("SELECT id, nombre, ubicacion, precio, descripcion FROM proyectos")
        proyectos = c.fetchall()
        conn.close()

        # Verificar si hay proyectos y devolverlos como JSON
        if proyectos:
            proyectos_list = [
                {
                    "id": proyecto[0],
                    "nombre": proyecto[1],
                    "ubicacion": proyecto[2],
                    "precio": proyecto[3],
                    "descripcion": proyecto[4]
                }
                for proyecto in proyectos
            ]
            return jsonify(proyectos_list)
        else:
            return jsonify({"message": "No se encontraron proyectos."}), 404

    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500   

@socketio.on("start_recording")
def start_recording():
    global recording_thread, recording_active
    if not recording_active:
        recording_active = True
        print("🚀 Iniciando grabación...")
        recording_thread = Thread(target=streamer.start_stream)
        recording_thread.start()
        emit("status", {"message": "Grabación iniciada."})
    else:
        emit("status", {"message": "La grabación ya está en curso."})

@socketio.on("stop_recording")
def stop_recording():
    global recording_active
    if recording_active:
        print("⏹️ Deteniendo grabación...")
        recording_active = False
        streamer.stop_stream()
        emit("status", {"message": "Grabación detenida."})
    else:
        emit("status", {"message": "No hay grabación en curso."})

# 🚀 Ejecutar servidor
if __name__ == "__main__":
    print("🌐 Levantando servidor Flask + SocketIO en puerto 5000")
    socketio.run(app, debug=True)
