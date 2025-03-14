# core/use_cases/emotion_analysis.py
from typing import Tuple, Optional
from ..entities import EmotionAnalysis, Transcription
from interfaces.emotion_detection import EmotionDetector

class EmotionAnalysisUseCase:
    def __init__(self, detector: EmotionDetector):
        self.detector = detector
        self._validation_threshold = 0.85  # Umbral de confianza mínimo
    
    def analyze_audio(self, audio_data: bytes) -> EmotionAnalysis:
        """
        Analiza un fragmento de audio y devuelve el análisis de emociones
        con validación de calidad del resultado
        """
        if not audio_data:
            raise ValueError("Datos de audio no pueden estar vacíos")
        
        raw_analysis = self.detector.analyze(audio_data)
        validated_analysis = self._validate_analysis(raw_analysis)
        
        return validated_analysis
    
    def analyze_transcription(self, transcription: Transcription) -> EmotionAnalysis:
        """
        Realiza análisis de emociones a partir de una transcripción existente
        aplicando reglas de negocio específicas
        """
        if transcription.confidence and transcription.confidence < 0.7:
            raise LowConfidenceError("La confianza de la transcripción es demasiado baja")
        
        return self.detector.analyze_text(transcription.text)
    
    def _validate_analysis(self, analysis: EmotionAnalysis) -> EmotionAnalysis:
        """Aplica reglas de validación de calidad del análisis"""
        total = sum([
            analysis.neutrality_prob,
            analysis.happiness_prob,
            analysis.anger_prob,
            analysis.unidentified_prob
        ])
        
        if abs(total - 1.0) > 0.01:
            raise InvalidAnalysisError("Las probabilidades no suman 1")
        
        if max([
            analysis.neutrality_prob,
            analysis.happiness_prob,
            analysis.anger_prob
        ]) < self._validation_threshold:
            analysis = analysis._replace(
                unidentified_prob=1 - sum([
                    analysis.neutrality_prob,
                    analysis.happiness_prob,
                    analysis.anger_prob
                ])
            )
        
        return analysis

class LowConfidenceError(Exception):
    """Error personalizado para confianza baja en transcripción"""

class InvalidAnalysisError(Exception):
    """Error para análisis que no cumple requisitos de calidad"""