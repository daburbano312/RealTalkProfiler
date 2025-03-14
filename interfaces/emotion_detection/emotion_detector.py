# interfaces/emotion_detection/emotion_detector.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, Dict
import logging

class EmotionDetectionError(Exception):
    """Excepción base para errores de detección de emociones"""
    pass

class InvalidAudioDataError(EmotionDetectionError):
    """Error cuando los datos de audio son inválidos"""
    pass

class UnsupportedLanguageError(EmotionDetectionError):
    """Error cuando el idioma no está soportado"""
    pass

class EmotionType(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    UNIDENTIFIED = "unidentified"

@dataclass(frozen=True)
class EmotionDetectionResult:
    predominant_emotion: EmotionType
    emotion_probabilities: Dict[EmotionType, float]
    audio_duration: Optional[float] = None
    text_length: Optional[int] = None
    confidence: Optional[float] = None
    detector_version: str = "1.0"

    def __post_init__(self):
        if sum(self.emotion_probabilities.values()) < 0.99:
            raise ValueError("Las probabilidades deben sumar aproximadamente 1")
            
        if self.confidence and not (0 <= self.confidence <= 1):
            raise ValueError("La confianza debe estar entre 0 y 1")

class EmotionDetector(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._supported_languages = ['es', 'en']
        self._current_language = 'es'

    @abstractmethod
    def analyze_audio(self, audio_data: bytes, sample_rate: int = 44100) -> EmotionDetectionResult:
        """
        Analiza emociones a partir de datos de audio crudos
        Args:
            audio_data: Bytes del audio a analizar
            sample_rate: Tasa de muestreo del audio
        Returns:
            EmotionDetectionResult: Resultado del análisis
        """
        pass

    @abstractmethod
    def analyze_text(self, text: str, language: str = 'es') -> EmotionDetectionResult:
        """
        Analiza emociones a partir de texto
        Args:
            text: Texto a analizar
            language: Idioma del texto (código ISO 639-1)
        Returns:
            EmotionDetectionResult: Resultado del análisis
        """
        pass

    @property
    @abstractmethod
    def supported_emotions(self) -> Tuple[EmotionType, ...]:
        """Devuelve la lista de emociones soportadas por el detector"""
        pass

    @abstractmethod
    def get_supported_languages(self) -> Tuple[str, ...]:
        """Devuelve los idiomas soportados para análisis de texto"""
        pass

    def set_language(self, language_code: str) -> None:
        """Configura el idioma para análisis de texto"""
        if language_code not in self._supported_languages:
            raise UnsupportedLanguageError(
                f"Idioma {language_code} no soportado. Idiomas disponibles: {', '.join(self._supported_languages)}"
            )
        self._current_language = language_code
        self.logger.info(f"Idioma configurado a: {language_code}")

    @abstractmethod
    def get_detector_metadata(self) -> Dict:
        """Obtiene metadatos sobre la implementación del detector"""
        pass

    def _validate_audio_input(self, audio_data: bytes, sample_rate: int) -> None:
        """Valida los parámetros de entrada de audio"""
        if not audio_data:
            raise InvalidAudioDataError("Los datos de audio no pueden estar vacíos")
        
        if sample_rate < 8000 or sample_rate > 48000:
            raise InvalidAudioDataError("Tasa de muestreo no soportada")

    def _validate_text_input(self, text: str) -> None:
        """Valida los parámetros de entrada de texto"""
        if len(text.strip()) < 10:
            raise ValueError("El texto debe contener al menos 10 caracteres")

    @abstractmethod
    def get_detector_type(self) -> str:
        """Devuelve el tipo de detector (audio/texto/multimodal)"""
        pass