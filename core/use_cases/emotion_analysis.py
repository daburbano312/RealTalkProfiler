from infrastructure.emotion.vokaturi_detector import VokaturiEmotionDetector
from infrastructure.emotion.openai_text_emotion_detector import OpenAITextEmotionDetector
from core.entities.emotion import EmotionAnalysis, EmotionType

class EmotionAnalysisUseCase:
    def __init__(self):
        self.audio_detector = VokaturiEmotionDetector()
        self.text_detector = OpenAITextEmotionDetector()

    def analyze_audio_and_text(self, audio_data: bytes, text: str) -> EmotionAnalysis:
        audio_emotion = self.audio_detector.analyze_audio(audio_data)
        text_emotion = self.text_detector.analyze_text(text)

        # Prioridad a la emoción del texto (OpenAI), más precisa.
        predominant_emotion = text_emotion.emotion_type if text_emotion.emotion_type != EmotionType.UNIDENTIFIED else audio_emotion.emotion_type

        final_analysis = EmotionAnalysis(
            emotion_type=predominant_emotion,
            neutrality_prob=(audio_emotion.neutrality_prob + text_emotion.neutrality_prob) / 2,
            happiness_prob=(audio_emotion.happiness_prob + text_emotion.happiness_prob) / 2,
            anger_prob=(audio_emotion.anger_prob + text_emotion.anger_prob) / 2,
            unidentified_prob=0.0
        )

        return final_analysis
