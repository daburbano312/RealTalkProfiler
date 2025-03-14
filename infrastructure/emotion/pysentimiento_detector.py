# infrastructure/emotion/pysentimiento_detector.py
from pysentimiento import create_analyzer
from typing import Dict
import logging
from interfaces.emotion_detection import (
    EmotionDetector,
    EmotionDetectionResult,
    EmotionType,
    EmotionDetectionError
)

class PysentimientoEmotionDetector(EmotionDetector):
    def __init__(self, lang: str = "es"):
        super().__init__()
        self.lang = lang
        self._analyzer = None
        self._load_model()

    def _load_model(self):
        try:
            self._analyzer = create_analyzer(task="emotion", lang=self.lang)
        except Exception as e:
            raise EmotionDetectionError(f"Failed to load pysentimiento model: {str(e)}")

    def analyze_text(self, text: str, language: str = None) -> EmotionDetectionResult:
        language = language or self.lang
        self._validate_text_input(text)
        self.set_language(language)
        
        try:
            result = self._analyzer.predict(text)
            return self._parse_result(result, text)
        except Exception as e:
            logging.error(f"Text analysis failed: {str(e)}")
            raise EmotionDetectionError("Text emotion detection failed") from e

    def analyze_audio(self, audio_data: bytes, sample_rate: int = None) -> EmotionDetectionResult:
        raise NotImplementedError("Pysentimiento detector only supports text analysis")

    def get_supported_emotions(self) -> tuple:
        return (
            EmotionType.ANGRY,
            EmotionType.HAPPY,
            EmotionType.SAD,
            EmotionType.FEAR,
            EmotionType.UNIDENTIFIED
        )

    def get_detector_metadata(self) -> Dict:
        return {
            "detector_type": "text",
            "model_name": "pysentimiento",
            "language": self.lang,
            "version": "0.7.1"
        }

    def _parse_result(self, result, text: str) -> EmotionDetectionResult:
        output = result.output
        probas = result.probas
        
        emotion_map = {
            "anger": EmotionType.ANGRY,
            "joy": EmotionType.HAPPY,
            "sadness": EmotionType.SAD,
            "fear": EmotionType.FEAR,
            "others": EmotionType.UNIDENTIFIED
        }
        
        emotion_probs = {
            emotion_map[k]: v for k, v in probas.items()
        }
        
        predominant = emotion_map[output]
        
        return EmotionDetectionResult(
            predominant_emotion=predominant,
            emotion_probabilities=emotion_probs,
            text_length=len(text),
            confidence=probas[output],
            detector_version=self.get_detector_metadata()["version"]
        )

    def get_detector_type(self) -> str:
        return "text"