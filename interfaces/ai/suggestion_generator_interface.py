from abc import ABC, abstractmethod
from core.entities.emotion import EmotionAnalysis

class SuggestionGeneratorInterface(ABC):
    @abstractmethod
    def generate_suggestions(self, emotion_analysis: EmotionAnalysis, context: str) -> str:
        pass
