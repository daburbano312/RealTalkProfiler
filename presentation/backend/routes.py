from flask import Blueprint, jsonify
from core.use_cases.audio_processing import AudioProcessingUseCase
from core.use_cases.suggestion_generation import SuggestionGenerationUseCase

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/process_audio", methods=["POST"])
def process_audio():
    audio_processor = AudioProcessingUseCase()
    suggestion_generator = SuggestionGenerationUseCase()

    transcription = audio_processor.process_audio()
    suggestions = suggestion_generator.generate_suggestions(transcription.emotion_analysis, context=transcription.text)

    response = {
        "transcription": transcription.to_dict(),
        "suggestions": suggestions
    }

    return jsonify(response)
