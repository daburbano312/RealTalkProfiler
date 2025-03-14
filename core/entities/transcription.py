# core/entities/transcription.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .emotion import EmotionAnalysis

@dataclass(frozen=True)
class Transcription:
    text: str
    emotion_analysis: EmotionAnalysis
    audio_duration: float
    timestamp: datetime = datetime.now()
    confidence: Optional[float] = None
    audio_source: Optional[str] = None

    def __post_init__(self):
        if len(self.text.strip()) == 0:
            raise ValueError("El texto de la transcripción no puede estar vacío")
        
        if self.audio_duration <= 0:
            raise ValueError("La duración del audio debe ser positiva")

    def to_dict(self):
        return {
            "text": self.text,
            "emotion": self.emotion_analysis.to_dict(),
            "audio_duration": self.audio_duration,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "audio_source": self.audio_source
        }