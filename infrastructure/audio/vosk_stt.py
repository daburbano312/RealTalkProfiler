# infrastructure/audio/vosk_stt.py
import vosk
import json
import logging
from typing import Generator, Tuple
from pathlib import Path
from interfaces.audio.speech_to_text import SpeechToText, TranscriptionConfig, TranscriptionResult
from core.entities.transcription import Transcription

class VoskSpeechToText(SpeechToText):
    def __init__(self, config: TranscriptionConfig = TranscriptionConfig()):
        super().__init__(config)
        self._model = None
        self._recognizer = None
        self._load_model()

    def _load_model(self):
        model_path = Path("models/vosk/es")
        if not model_path.exists():
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
            
        try:
            self._model = vosk.Model(str(model_path))
            self._recognizer = vosk.KaldiRecognizer(self._model, self.config.sample_rate)
        except Exception as e:
            logging.error(f"Failed to load Vosk model: {str(e)}")
            raise

    def transcribe(self, audio_data: bytes) -> Transcription:
        self._validate_audio_input(audio_data)
        
        try:
            if self._recognizer.AcceptWaveform(audio_data):
                result = json.loads(self._recognizer.Result())
                return self._create_transcription(
                    result['text'],
                    result.get('conf', 0.0),
                    len(audio_data) / (2 * self.config.sample_rate)
                )
            return self._create_transcription("", 0.0, 0.0)
        except Exception as e:
            logging.error(f"Transcription failed: {str(e)}")
            return self._create_transcription("Error en transcripción", 0.0, 0.0)

    def transcribe_streaming(self, audio_stream: Generator[bytes, None, None]) -> Generator[TranscriptionResult, None, None]:
        for chunk in audio_stream:
            if self._recognizer.AcceptWaveform(chunk):
                result = json.loads(self._recognizer.Result())
                yield TranscriptionResult(
                    text=result['text'],
                    confidence=result.get('conf'),
                    is_final=True
                )
            else:
                partial = json.loads(self._recognizer.PartialResult())
                yield TranscriptionResult(
                    text=partial.get('partial', ''),
                    confidence=None,
                    is_final=False
                )

    def transcribe_file(self, file_path: str) -> Transcription:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        return self.transcribe(audio_data)

    def get_supported_languages(self) -> Tuple[str, ...]:
        return ('es', 'en')

    def set_language(self, language_code: str) -> None:
        self._validate_language(language_code)
        self._load_model()

    def _create_transcription(self, text: str, confidence: float, duration: float) -> Transcription:
        return self.create_transcription_object(
            text=text,
            confidence=confidence,
            audio_duration=duration
        )

    def _validate_audio_input(self, audio_data: bytes):
        if len(audio_data) < 1024:
            raise ValueError("Audio data too short")