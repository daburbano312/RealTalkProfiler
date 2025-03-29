from openai import OpenAI
from config.settings import settings
from interfaces.ai.suggestion_interface import SuggestionGeneratorInterface
from core.entities.emotion import EmotionAnalysis

class OpenAISuggestionGenerator(SuggestionGeneratorInterface):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_suggestions(self, emotion_analysis: EmotionAnalysis, context: str) -> list[str]:
        prompt = (
            f"Eres un terapeuta emocional. La persona habló y el sistema detectó estas emociones:\n"
            f"- Neutralidad: {emotion_analysis.neutrality_prob:.2f}\n"
            f"- Felicidad: {emotion_analysis.happiness_prob:.2f}\n"
            f"- Enojo: {emotion_analysis.anger_prob:.2f}\n"
            f"- Miedo/Indefinido: {emotion_analysis.unidentified_prob:.2f}\n\n"
            f"Texto de la persona: \"{context}\"\n\n"
            f"Con base en esto, da una sugerencia amable y empática para ayudar a mejorar su estado emocional. Responde con una sola frase."
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un terapeuta emocional útil y empático."},
                {"role": "user", "content": prompt}
            ]
        )

        suggestion = response.choices[0].message.content.strip()
        return [suggestion]
