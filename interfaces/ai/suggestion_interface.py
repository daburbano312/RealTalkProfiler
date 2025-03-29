from abc import ABC, abstractmethod
from core.entities.suggestion import Suggestion
from core.entities.emotion import EmotionAnalysis
from typing import List

class SuggestionGeneratorInterface(ABC):

    @abstractmethod
    def generate_suggestions(self, emotion_analysis: EmotionAnalysis, context: str = "") -> List[Suggestion]:
        pass
