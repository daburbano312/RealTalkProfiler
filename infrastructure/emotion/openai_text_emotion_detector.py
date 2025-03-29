from openai import OpenAI
from interfaces.emotion_detection.emotion_interface import EmotionDetectionInterface
from core.entities.emotion import EmotionAnalysis, EmotionType
from config.settings import settings

class OpenAITextEmotionDetector(EmotionDetectionInterface):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_text(self, text: str) -> EmotionAnalysis:
        prompt = (
            f"Analiza el siguiente texto y responde solo con una de las siguientes emociones: "
            f"Happy, Angry, Neutral.\nTexto: \"{text}\""
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un analizador de emociones."},
                {"role": "user", "content": prompt}
            ]
        )

        emotion_str = response.choices[0].message.content.strip().lower()

        return EmotionAnalysis(
            emotion_type=self._map_emotion_type(emotion_str),
            neutrality_prob=1.0 if "neutral" in emotion_str else 0.0,
            happiness_prob=1.0 if "happy" in emotion_str else 0.0,
            anger_prob=1.0 if "angry" in emotion_str else 0.0,
            unidentified_prob=0.0
        )

    def analyze_audio(self, audio_data: bytes) -> EmotionAnalysis:
        raise NotImplementedError("Este detector solo analiza texto.")

    def _map_emotion_type(self, emotion_str: str) -> EmotionType:
        if "happy" in emotion_str:
            return EmotionType.HAPPY
        elif "angry" in emotion_str:
            return EmotionType.ANGRY
        else:
            return EmotionType.NEUTRAL
