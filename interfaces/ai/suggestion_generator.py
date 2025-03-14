# interfaces/ai/suggestion_generator.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import logging
from datetime import datetime
from core.entities.emotion import EmotionType, EmotionAnalysis
from core.entities.transcription import Transcription

class SuggestionGenerationError(Exception):
    """Excepción base para errores de generación de sugerencias"""
    pass

class InvalidInputError(SuggestionGenerationError):
    """Error cuando los parámetros de entrada son inválidos"""
    pass

class ModelOverloadError(SuggestionGenerationError):
    """Error cuando el modelo está sobrecargado"""
    pass

class SuggestionType(Enum):
    STANDARD = "standard"
    PROACTIVE = "proactive"
    MITIGATION = "mitigation"
    ESCALATION = "escalation"

@dataclass(frozen=True)
class Suggestion:
    text: str
    suggestion_type: SuggestionType
    target_emotion: EmotionType
    confidence: float
    generation_date: datetime = datetime.now()
    metadata: Optional[Dict] = None

    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError("La confianza debe estar entre 0 y 1")
        
        if len(self.text.strip()) < 10:
            raise ValueError("El texto de sugerencia es demasiado corto")

class SuggestionGenerator(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._max_suggestions = 5
        self._min_confidence = 0.5

    @abstractmethod
    def generate_from_emotion(
        self,
        emotion_analysis: EmotionAnalysis,
        context: Optional[Dict] = None
    ) -> List[Suggestion]:
        """
        Genera sugerencias basadas en análisis de emociones
        Args:
            emotion_analysis: Resultado del análisis de emociones
            context: Contexto adicional para la generación
        Returns:
            Lista de sugerencias ordenadas por relevancia
        """
        pass

    @abstractmethod
    def generate_from_text(
        self,
        text: str,
        language: str = "es",
        context: Optional[Dict] = None
    ) -> List[Suggestion]:
        """
        Genera sugerencias basadas en texto de entrada
        Args:
            text: Texto a analizar
            language: Idioma del texto (código ISO 639-1)
            context: Contexto adicional para la generación
        Returns:
            Lista de sugerencias ordenadas por relevancia
        """
        pass

    @abstractmethod
    def generate_from_transcription(
        self,
        transcription: Transcription
    ) -> List[Suggestion]:
        """
        Genera sugerencias basadas en una transcripción completa
        Args:
            transcription: Objeto Transcription con metadatos
        Returns:
            Lista de sugerencias contextuales
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Devuelve lista de idiomas soportados"""
        pass

    @abstractmethod
    def model_version(self) -> str:
        """Devuelve versión del modelo utilizado"""
        pass

    @abstractmethod
    def get_max_suggestions(self) -> int:
        """Devuelve el número máximo de sugerencias a generar"""
        pass

    @abstractmethod
    def set_generation_parameters(
        self,
        temperature: float = 0.7,
        max_length: int = 100,
        creativity: float = 0.5
    ) -> None:
        """Configura parámetros de generación del modelo"""
        pass

    def _validate_inputs(
        self,
        text: Optional[str] = None,
        emotion_analysis: Optional[EmotionAnalysis] = None
    ) -> None:
        """Valida los parámetros de entrada comunes"""
        if text and len(text.strip()) < 5:
            raise InvalidInputError("El texto de entrada es demasiado corto")
            
        if emotion_analysis and not isinstance(emotion_analysis, EmotionAnalysis):
            raise InvalidInputError("Análisis de emociones inválido")

    def _apply_business_rules(
        self,
        suggestions: List[Suggestion]
    ) -> List[Suggestion]:
        """Aplica reglas de negocio a las sugerencias generadas"""
        return sorted(
            [s for s in suggestions if s.confidence >= self._min_confidence],
            key=lambda x: (-x.confidence, x.suggestion_type.value)
        )[:self._max_suggestions]

    @abstractmethod
    def get_performance_metrics(self) -> Dict:
        """Obtiene métricas de rendimiento del generador"""
        pass