from flask import Blueprint, jsonify
from core.use_cases.audio_processing import AudioProcessingUseCase
from core.use_cases.suggestion_generation import SuggestionGenerationUseCase

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200

@api_blueprint.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        audio_processor = AudioProcessingUseCase()
        suggestion_generator = SuggestionGenerationUseCase()

        transcription = audio_processor.process_audio_automatic(seconds=6)

        suggestions = suggestion_generator.generate_suggestions(
            transcription.emotion_analysis,
            context=transcription.text
        )

        emotions = transcription.emotion_analysis.to_dict()

        print("📄 Transcripción (texto):", transcription.text)
        print("🎭 Tipo de emoción:", emotions["emotion_type"])
        print("📊 Valores de emoción:", emotions)
        print("💡 Sugerencias:", suggestions)

        response = {
            "transcription": transcription.text,
            "audio_emotion": emotions["emotion_type"],
            "neutrality": emotions["neutrality"],
            "happiness": emotions["happiness"],
            "anger": emotions["anger"],
            "suggestions": suggestions
        }

        return jsonify(response), 200

    except Exception as e:
        print("❌ Error en /process_audio:", e)
        return jsonify({
            "error": "Error interno en el servidor",
            "details": str(e)
        }), 500
