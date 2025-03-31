from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .emotion import EmotionAnalysis

@dataclass(frozen=True)
class Transcription:
    text: str
    emotion_analysis: EmotionAnalysis
    audio_duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: Optional[float] = None

    def to_dict(self):
        return {
            "text": self.text,
            "emotion": self.emotion_analysis.to_dict(),
            "audio_duration": self.audio_duration,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence
        }
