# presentation/web/app.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO 
from infrastructure.audio.vosk_stt import VoskSpeechToText
from infrastructure.audio.vokaturi_recorder import VokaturiRecorder
from infrastructure.emotion.vokaturi_detector import VokaturiEmotionDetector
from infrastructure.ai.openai_generator import OpenAIGenerator
from core.use_cases import (
    AudioProcessingUseCase,
    EmotionAnalysisUseCase,
    SuggestionGenerationUseCase
)
import os

def create_app(config=None):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Configuración
    app.config.from_mapping(
        VOKATURI_DLL_PATH=os.getenv('VOKATURI_DLL', 'libs/OpenVokaturi-4-0-win64.dll'),
        OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
        AUDIO_SAMPLE_RATE=16000,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB
    )

    # Inicialización de dependencias
    with app.app_context():
        # Infraestructura
        stt_service = VoskSpeechToText()
        recorder = VokaturiRecorder(dll_path=app.config['VOKATURI_DLL_PATH'])
        emotion_detector = VokaturiEmotionDetector(
            dll_path=app.config['VOKATURI_DLL_PATH']  # <-- Añadir este parámetro
            )
        suggestion_generators = [
            OpenAIGenerator(api_key=app.config['OPENAI_API_KEY'])
        ]

        # Casos de uso
        audio_processor = AudioProcessingUseCase(stt_service)
        emotion_analyzer = EmotionAnalysisUseCase(emotion_detector)
        suggestion_generator = SuggestionGenerationUseCase(suggestion_generators)

        # Registrar rutas
        from .routes import configure_routes
        configure_routes(app, socketio, audio_processor, emotion_analyzer, suggestion_generator)

    return app

if __name__ == "__main__":
    app = create_app()
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)


