from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread
import os

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

# 🔤 Transcripción
speech_to_text = VoskSpeechToText()
transcriber = TranscriptionUseCase(speech_to_text)

# 📞 Procesamiento de audio
def handle_audio(audio_chunk):
    global emotion_word_buffer

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

# 🚀 Ejecutar servidor
if __name__ == "__main__":
    print("🚀 Iniciando transcripción en hilo separado...")
    thread = Thread(target=streamer.start_stream)
    thread.start()

    print("🌐 Levantando servidor Flask + SocketIO en puerto 5000")
    socketio.run(app, debug=True)
