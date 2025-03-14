# core/entities/emotion.py
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

    def __post_init__(self):
        if not (0 <= self.neutrality_prob <= 1 and
                0 <= self.happiness_prob <= 1 and
                0 <= self.anger_prob <= 1 and
                0 <= self.unidentified_prob <= 1):
            raise ValueError("Las probabilidades deben estar entre 0 y 1")
            
        total = sum([self.neutrality_prob, 
                    self.happiness_prob, 
                    self.anger_prob,
                    self.unidentified_prob])
        
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Las probabilidades deben sumar 1 (actual: {total:.2f})")

    def to_dict(self):
        return {
            "emotion_type": self.emotion_type.value,
            "neutrality": self.neutrality_prob,
            "happiness": self.happiness_prob,
            "anger": self.anger_prob,
            "unidentified": self.unidentified_prob
        }