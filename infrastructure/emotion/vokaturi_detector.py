# infrastructure/emotion/vokaturi_detector.py
import Vokaturi
import numpy as np
import logging
from typing import Dict
from datetime import datetime
from interfaces.emotion_detection import (
    EmotionDetector,
    EmotionDetectionResult,
    EmotionType,
    EmotionDetectionError,
    InvalidAudioDataError
)

class VokaturiEmotionDetector(EmotionDetector):
    def __init__(self, sample_rate: int = 44100, buffer_length: int = 1024, dll_path: str = ""):
        super().__init__()
        self.sample_rate = sample_rate
        self.buffer_length = buffer_length
        self._voice = None
        self._load_library(dll_path)

    def _load_library(self, dll_path: str):
        try:
            Vokaturi.load(dll_path)
            self._voice = Vokaturi.Voice(
                self.sample_rate,
                self.buffer_length,
                True
            )
        except Exception as e:
            raise EmotionDetectionError(f"Error loading Vokaturi library: {str(e)}")

    def analyze_audio(self, audio_data: bytes, sample_rate: int = None) -> EmotionDetectionResult:
        sample_rate = sample_rate or self.sample_rate
        self._validate_audio_input(audio_data, sample_rate)

        try:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            self._voice.fill_float32array(len(audio_array), audio_array)
            
            quality = Vokaturi.Quality()
            probabilities = Vokaturi.EmotionProbabilities()
            self._voice.extract(quality, probabilities)
            
            if not quality.valid:
                raise InvalidAudioDataError("Audio quality insufficient for analysis")
            
            return self._create_result(probabilities, len(audio_data) / sample_rate)
            
        except Exception as e:
            logging.error(f"Vokaturi analysis failed: {str(e)}")
            raise EmotionDetectionError("Emotion detection failed") from e

    def analyze_text(self, text: str, language: str = 'es') -> EmotionDetectionResult:
        raise NotImplementedError("Vokaturi detector only supports audio analysis")

    def get_supported_emotions(self) -> tuple:
        return (
            EmotionType.NEUTRAL,
            EmotionType.HAPPY,
            EmotionType.SAD,
            EmotionType.ANGRY,
            EmotionType.FEAR
        )

    def get_detector_metadata(self) -> Dict:
        return {
            "detector_type": "audio",
            "version": Vokaturi.versionAndLicense(),
            "sample_rate": self.sample_rate,
            "buffer_length": self.buffer_length
        }

    def _create_result(self, probabilities, duration: float) -> EmotionDetectionResult:
        emotion_probs = {
            EmotionType.NEUTRAL: probabilities.neutrality,
            EmotionType.HAPPY: probabilities.happiness,
            EmotionType.SAD: probabilities.sadness,
            EmotionType.ANGRY: probabilities.anger,
            EmotionType.FEAR: probabilities.fear
        }
        
        predominant = max(emotion_probs, key=emotion_probs.get)
        
        return EmotionDetectionResult(
            predominant_emotion=predominant,
            emotion_probabilities=emotion_probs,
            audio_duration=duration,
            confidence=emotion_probs[predominant],
            detector_version=self.get_detector_metadata()["version"]
        )

    def get_detector_type(self) -> str:
        return "audio"

    # **Métodos agregados para corregir el error**
    def get_supported_languages(self) -> tuple:
        """Devuelve los idiomas soportados para análisis de texto"""
        return ("es", "en")  # Agrega los idiomas realmente soportados

    @property
    def supported_emotions(self) -> tuple:
        """Devuelve la lista de emociones soportadas"""
        return (
            EmotionType.NEUTRAL,
            EmotionType.HAPPY,
            EmotionType.SAD,
            EmotionType.ANGRY,
            EmotionType.FEAR
        )
