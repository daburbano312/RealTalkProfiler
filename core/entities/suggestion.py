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

    def to_dict(self):
        return {
            "suggestion_text": self.text,
            "target_emotion": self.emotion_type.value,
            "context": self.context,
            "priority": self.priority,
            "generated_at": self.generated_at.isoformat()
        }
