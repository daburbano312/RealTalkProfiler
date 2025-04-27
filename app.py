from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread
import os
import sqlite3
from flask_cors import CORS
from dotenv import load_dotenv

# Core y capas
from core.use_cases.transcribe_stream import TranscriptionUseCase
from core.use_cases.manage_history_use_case import ManageHistoryUseCase
from core.use_cases.get_history_use_case import GetHistoryUseCase
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from infrastructure.history.history_repository import HistoryRepository
from interfaces.audio.audio_streamer import AudioStreamer
from infrastructure.emotion.text_emotion_detector import TextEmotionAnalyzer
from infrastructure.emotion.keyword_extractor import KeywordExtractor
from infrastructure.ai.openai_recommendation_engine import OpenAIRecommendationEngine

# Cargar variables de entorno
load_dotenv()

# 🧠 Módulos de análisis
text_emotion_analyzer = TextEmotionAnalyzer()
keyword_extractor = KeywordExtractor()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ No se encontró la variable de entorno OPENAI_API_KEY. Verifica tu archivo .env o el entorno.")

recommendation_engine = OpenAIRecommendationEngine(api_key=openai_api_key)

# 🗃️ Historial
history_repo = HistoryRepository()
manage_history_use_case = ManageHistoryUseCase(history_repo)
get_history_use_case = GetHistoryUseCase(history_repo)

# 🔧 Configuración de Flask
app = Flask(__name__, template_folder="presentation/web/templates", static_folder="presentation/web/static")
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# 🔤 Transcripción
speech_to_text = VoskSpeechToText()
transcriber = TranscriptionUseCase(speech_to_text)

# 📋 Variables globales
recording_thread = None
recording_active = False
streamer = None  # 🚨 Importante: inicializamos en None
current_client_id = None
current_call_name = None
emotion_word_buffer = []
MAX_EMOTION_WORDS = 15

# 📞 Procesamiento de audio
def handle_audio(audio_chunk):
    global emotion_word_buffer, recording_active, current_client_id, current_call_name

    if not recording_active:
        return

    if speech_to_text.accept_waveform(audio_chunk):
        result = speech_to_text.get_result()
        text = result.get("text", "").strip()

        if text:
            print(f"✅ Texto final: {text}")
            socketio.emit("transcription", text)
            manage_history_use_case.add_transcription(current_client_id, current_call_name, text)

            words = text.split()
            emotion_word_buffer += words
            print(f"🧠 Palabras acumuladas: {len(emotion_word_buffer)}")

            if len(emotion_word_buffer) >= MAX_EMOTION_WORDS:
                full_text = " ".join(emotion_word_buffer[:MAX_EMOTION_WORDS])

                emotion_result = text_emotion_analyzer.analyze(full_text)
                print(f"🎭 Emoción detectada: {emotion_result['emotion']}")
                socketio.emit("emotion", emotion_result)
                manage_history_use_case.add_emotion(current_client_id, current_call_name, emotion_result['emotion'], emotion_result.get('score', 1.0))

                keywords = keyword_extractor.extract_keywords(full_text)
                print(f"🔑 Palabras clave: {keywords}")
                socketio.emit("keywords", {"keywords": keywords})

                suggestion = recommendation_engine.generate_advice(emotion_result['emotion'], keywords, full_text)
                print(f"📢 Sugerencia generada: {suggestion}")
                socketio.emit("suggestion", {"text": suggestion})
                manage_history_use_case.add_suggestion(current_client_id, current_call_name, suggestion)

                emotion_word_buffer = emotion_word_buffer[MAX_EMOTION_WORDS:]

# 🌎 Rutas web
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/proyectos")
def proyectos():
    return render_template("projects.html")

@app.route("/api/proyectos", methods=["GET"])
def obtener_proyectos():
    try:
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()
        c.execute("SELECT id, nombre, ubicacion, precio, descripcion FROM proyectos")
        proyectos = c.fetchall()
        conn.close()

        if proyectos:
            proyectos_list = [
                {"id": proyecto[0], "nombre": proyecto[1], "ubicacion": proyecto[2], "precio": proyecto[3], "descripcion": proyecto[4]}
                for proyecto in proyectos
            ]
            return jsonify(proyectos_list)
        else:
            return jsonify({"message": "No se encontraron proyectos."}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500

# 📜 Nueva Ruta para consultar el historial de un cliente
@app.route("/api/historial/<client_id>", methods=["GET"])
def obtener_historial_cliente(client_id):
    historial = get_history_use_case.get_client_history(client_id)
    if historial:
        return jsonify(historial.to_dict())
    else:
        return jsonify({"message": "No se encontró historial para este cliente."}), 404

# 🌐 WebSockets
@socketio.on("connect")
def connect():
    print("✅ Cliente conectado vía WebSocket")

@socketio.on("start_recording")
def start_recording(data=None):
    global recording_thread, recording_active, current_client_id, current_call_name, streamer

    if data and "client_id" in data:
        client_id_input = data["client_id"]
    else:
        client_id_input = "cliente_demo"

    if not recording_active:
        # 🛠️ RECREAR el streamer nuevo en cada grabación
        streamer = AudioStreamer(lambda chunk: handle_audio(chunk))

        recording_active = True
        current_client_id = client_id_input
        current_call_name = manage_history_use_case.start_new_call(current_client_id)

        print(f"🚀 Iniciando grabación para cliente {current_client_id}...")
        recording_thread = Thread(target=streamer.start_stream)
        recording_thread.start()
        emit("status", {"message": f"Grabación iniciada para cliente {current_client_id}."})
    else:
        emit("status", {"message": "La grabación ya está en curso."})

@socketio.on("stop_recording")
def stop_recording():
    global recording_active, streamer
    if recording_active:
        print("⏹️ Deteniendo grabación...")
        recording_active = False

        if streamer and streamer.stream:
            streamer.stop_stream()
            del streamer.stream  # 🛠️ Liberar memoria del stream
            streamer.stream = None

        emit("status", {"message": "Grabación detenida."})
    else:
        emit("status", {"message": "No hay grabación en curso."})

# 🚀 Ejecutar servidor
if __name__ == "__main__":
    print("🌐 Levantando servidor Flask + SocketIO en puerto 5000")
    socketio.run(app, debug=True)
