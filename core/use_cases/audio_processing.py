# core/use_cases/audio_processing.py
import logging
from typing import List, Tuple
from ..entities import Transcription
from interfaces.audio import SpeechToText

class AudioProcessingUseCase:
    def __init__(self, stt_service: SpeechToText):
        self.stt_service = stt_service
        self.logger = logging.getLogger(__name__)
    
    def process_audio(self, audio_data: bytes) -> Transcription:
        """Procesa audio completo y devuelve transcripción con metadatos"""
        try:
            result = self.stt_service.transcribe(audio_data)
            return self._create_transcription_object(result)
        except Exception as e:
            self.logger.error(f"Error en procesamiento de audio: {str(e)}")
            raise AudioProcessingError("Falló el procesamiento de audio") from e
    
    def process_streaming_audio(self, audio_chunks: List[bytes]) -> Tuple[List[Transcription], float]:
        """Procesa audio en streaming con gestión de contexto"""
        transcriptions = []
        total_duration = 0.0
        
        for chunk in audio_chunks:
            transcription = self.stt_service.transcribe(chunk)
            total_duration += transcription.audio_duration
            transcriptions.append(transcription)
        
        return transcriptions, total_duration
    
    def _create_transcription_object(self, raw_result: dict) -> Transcription:
        """Factory method para crear objeto Transcription validado"""
        return Transcription(
            text=raw_result['text'],
            emotion_analysis=raw_result.get('emotion_analysis'),
            audio_duration=raw_result['duration'],
            confidence=raw_result.get('confidence', 0.0),
            audio_source=raw_result.get('source')
        )

class AudioProcessingError(Exception):
    """Error personalizado para fallos en procesamiento de audio"""