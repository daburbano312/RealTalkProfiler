# core/entities/suggestion.py
from dataclasses import dataclass
from datetime import datetime
from .emotion import EmotionType

@dataclass(frozen=True)
class Suggestion:
    text: str
    emotion_type: EmotionType
    context: str
    priority: int = 1
    generated_at: datetime = datetime.now()

    def __post_init__(self):
        if len(self.text.strip()) == 0:
            raise ValueError("El texto de sugerencia no puede estar vacío")
        
        if self.priority < 1 or self.priority > 5:
            raise ValueError("La prioridad debe estar entre 1 y 5")

    def to_dict(self):
        return {
            "suggestion_text": self.text,
            "target_emotion": self.emotion_type.value,
            "context": self.context,
            "priority": self.priority,
            "generated_at": self.generated_at.isoformat()
        }

@dataclass(frozen=True)
class SuggestionHistory:
    suggestions: tuple[Suggestion, ...]
    
    def get_latest(self, n: int = 3) -> list[Suggestion]:
        return sorted(
            self.suggestions, 
            key=lambda x: x.generated_at, 
            reverse=True
        )[:n]

    def filter_by_emotion(self, emotion_type: EmotionType) -> list[Suggestion]:
        return [s for s in self.suggestions if s.emotion_type == emotion_type]