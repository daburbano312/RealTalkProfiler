from abc import ABC, abstractmethod
from core.entities.emotion import EmotionAnalysis

class EmotionDetectionInterface(ABC):

    @abstractmethod
    def analyze_audio(self, audio_data: bytes) -> EmotionAnalysis:
        pass

    @abstractmethod
    def analyze_text(self, text: str) -> EmotionAnalysis:
        pass
