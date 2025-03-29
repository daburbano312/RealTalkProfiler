from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    NEUTRAL = "Neutral"
    HAPPY = "Feliz"
    ANGRY = "Enojado"
    UNIDENTIFIED = "NoIdentificado"

@dataclass(frozen=True)
class EmotionAnalysis:
    emotion_type: EmotionType
    neutrality_prob: float
    happiness_prob: float
    anger_prob: float
    unidentified_prob: float = 0.0

    def to_dict(self):
        return {
            "emotion_type": self.emotion_type.value,
            "neutrality": self.neutrality_prob,
            "happiness": self.happiness_prob,
            "anger": self.anger_prob,
            "unidentified": self.unidentified_prob
        }
