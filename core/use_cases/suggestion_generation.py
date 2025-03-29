from infrastructure.ai.openai_suggestion_generator import OpenAISuggestionGenerator
from core.entities.suggestion import Suggestion
from core.entities.emotion import EmotionAnalysis
from typing import List

class SuggestionGenerationUseCase:
    def __init__(self):
        self.generator = OpenAISuggestionGenerator()

    def generate_suggestions(self, emotion_analysis: EmotionAnalysis, context: str = "") -> List[Suggestion]:
        return self.generator.generate_suggestions(emotion_analysis, context)
