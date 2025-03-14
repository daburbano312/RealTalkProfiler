# interfaces/audio/speech_to_text.py
from abc import ABC, abstractmethod
from typing import Optional, Union, Generator, Tuple
from dataclasses import dataclass
import logging
from core.entities.transcription import Transcription

class TranscriptionError(Exception):
    """Excepción base para errores de transcripción"""
    pass

class LanguageNotSupportedError(TranscriptionError):
    """Error cuando el idioma no está soportado"""
    pass

@dataclass(frozen=True)
class TranscriptionConfig:
    language: str = 'es-ES'
    interim_results: bool = True
    max_alternatives: int = 1
    word_confidence: bool = False
    speaker_diarization: bool = False
    sample_rate: int = 16000  # Añade este atributo

@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    confidence: Optional[float]
    language: str
    is_final: bool = True
    alternatives: Tuple[str, ...] = ()

class SpeechToText(ABC):
    def __init__(self, config: TranscriptionConfig = TranscriptionConfig()):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> Transcription:
        """Transcribe audio completo a texto"""
        pass

    @abstractmethod
    def transcribe_streaming(
        self, 
        audio_stream: Generator[bytes, None, None]
    ) -> Generator[TranscriptionResult, None, None]:
        """Transcribe un stream de audio en tiempo real"""
        pass

    @abstractmethod
    def transcribe_file(self, file_path: str) -> Transcription:
        """Transcribe un archivo de audio directamente"""
        pass

    @abstractmethod
    def get_supported_languages(self) -> Tuple[str, ...]:
        """Obtiene lista de idiomas soportados"""
        pass

    @abstractmethod
    def set_language(self, language_code: str) -> None:
        """Configura el idioma para transcripción"""
        pass

    def _validate_language(self, language_code: str) -> bool:
        """Valida que el idioma esté soportado"""
        supported = self.get_supported_languages()
        if language_code not in supported:
            raise LanguageNotSupportedError(
                f"Idioma {language_code} no soportado. Idiomas disponibles: {', '.join(supported)}"
            )
        return True

    def create_transcription_object(
        self,
        text: str,
        confidence: Optional[float],
        audio_duration: float
    ) -> Transcription:
        """Factory method para crear objetos Transcription"""
        return Transcription(
            text=text,
            confidence=confidence,
            audio_duration=audio_duration,
            audio_source=self.__class__.__name__
        )