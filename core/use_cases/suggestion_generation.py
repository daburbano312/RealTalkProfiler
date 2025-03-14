# core/use_cases/suggestion_generation.py
from typing import List
from ..entities import Suggestion, EmotionAnalysis, Transcription
from interfaces.ai import SuggestionGenerator

class SuggestionGenerationUseCase:
    def __init__(self, generators: List[SuggestionGenerator]):
        self.generators = generators
        self._priority_rules = {
            'Enojado': 5,
            'Feliz': 3,
            'Neutral': 2,
            'NoIdentificado': 1
        }
    
    def generate_from_emotion(self, analysis: EmotionAnalysis, context: str = "") -> List[Suggestion]:
        """Genera sugerencias basadas en análisis de emociones con priorización"""
        suggestions = []
        
        for generator in self.generators:
            try:
                raw_suggestions = generator.generate(analysis, context)
                prioritized = self._apply_priority_rules(raw_suggestions)
                suggestions.extend(prioritized)
            except Exception as e:
                continue  # Fail silently for non-critical generators
        
        return sorted(suggestions, key=lambda x: x.priority, reverse=True)[:3]
    
    def generate_from_transcription(self, transcription: Transcription) -> List[Suggestion]:
        """Genera sugerencias contextuales basadas en transcripción completa"""
        context = self._extract_context(transcription.text)
        return self.generate_from_emotion(transcription.emotion_analysis, context)
    
    def _apply_priority_rules(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """Aplica reglas de negocio para priorización de sugerencias"""
        for suggestion in suggestions:
            new_priority = self._priority_rules.get(
                suggestion.emotion_type.value, 
                suggestion.priority
            )
            suggestion.priority = max(new_priority, suggestion.priority)
        
        return suggestions
    
    def _extract_context(self, text: str) -> str:
        """Extrae contexto clave del texto para generar sugerencias relevantes"""
        keywords = {'cuenta', 'pago', 'problema', 'información', 'servicio'}
        found = [word for word in text.lower().split() if word in keywords]
        return " ".join(found) if found else "general"

class SuggestionGenerationError(Exception):
    """Error personalizado para fallos en generación de sugerencias"""