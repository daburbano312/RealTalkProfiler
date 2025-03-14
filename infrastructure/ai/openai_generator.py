# infrastructure/ai/openai_generator.py
import openai
from datetime import datetime
from typing import List, Dict, Optional
import logging
from core.entities import EmotionAnalysis, Transcription, Suggestion, EmotionType
from interfaces.ai.suggestion_generator import (
    SuggestionGenerator,
    SuggestionType,
    SuggestionGenerationError,
    ModelOverloadError,
    InvalidInputError
)
from openai import OpenAI


class OpenAIGenerator(SuggestionGenerator):
    def __init__(self, api_key: str, default_model: str = "gpt-4-turbo"):
        super().__init__()
        self.client = OpenAI(api_key=api_key)
        self.default_model = default_model
        self._temperature = 0.7
        self._max_tokens = 300
        self._creativity = 0.5
        self._max_suggestions = 5
        self._request_count = 0
        
        # Plantillas de prompts en múltiples idiomas
        self.prompt_templates = {
            'es': {
                'emotion': (
                    "Eres un asistente para agentes de call center. Genera {num} sugerencias profesionales "
                    "basadas en la emoción detectada: {emotion} (confianza: {confidence:.0%}). "
                    "Contexto adicional: {context}. Formato: • [Tipo] Sugerencia corta"
                ),
                'text': (
                    "Analiza el siguiente mensaje del cliente y genera {num} sugerencias de acción "
                    "para el agente: '{text}'. Contexto: {context}. Formato: • [Tipo] Sugerencia"
                )
            },
            'en': {
                'emotion': (
                    "You're a call center assistant. Generate {num} professional suggestions "
                    "based on detected emotion: {emotion} (confidence: {confidence:.0%}). "
                    "Additional context: {context}. Format: • [Type] Short suggestion"
                )
            }
        }

    def generate_from_emotion(
        self, 
        emotion_analysis: EmotionAnalysis,
        context: Optional[Dict] = None
    ) -> List[Suggestion]:
        self._validate_inputs(emotion_analysis=emotion_analysis)
        context_str = self._parse_context(context)
        
        try:
            prompt = self._build_emotion_prompt(emotion_analysis, context_str)
            response = self._call_openai_api(prompt)
            return self._parse_suggestions(response, emotion_analysis.predominant_emotion)
        except openai.RateLimitError as e:
            raise ModelOverloadError("Límite de tasa excedido") from e
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise SuggestionGenerationError("Error generando sugerencias") from e

    def generate_from_text(
        self, 
        text: str,
        language: str = "es",
        context: Optional[Dict] = None
    ) -> List[Suggestion]:
        self._validate_inputs(text=text)
        context_str = self._parse_context(context)
        
        try:
            prompt = self._build_text_prompt(text, context_str, language)
            response = self._call_openai_api(prompt)
            return self._parse_suggestions(response, None)
        except openai.APIError as e:
            raise ModelOverloadError("Error en API de OpenAI") from e

    def generate_from_transcription(self, transcription: Transcription) -> List[Suggestion]:
        return self.generate_from_text(
            text=transcription.text,
            context={
                'emotion': transcription.emotion_analysis.predominant_emotion.value,
                'duration': transcription.audio_duration
            }
        )

    def get_supported_languages(self) -> List[str]:
        return ['es', 'en']

    def model_version(self) -> str:
        return self.default_model

    def get_max_suggestions(self) -> int:
        return self._max_suggestions

    def set_generation_parameters(
        self,
        temperature: float = 0.7,
        max_length: int = 300,
        creativity: float = 0.5
    ) -> None:
        self._temperature = max(0.1, min(temperature, 1.0))
        self._max_tokens = max(100, min(max_length, 1000))
        self._creativity = creativity

    def get_performance_metrics(self) -> Dict:
        return {
            'requests': self._request_count,
            'model': self.default_model,
            'parameters': {
                'temperature': self._temperature,
                'max_tokens': self._max_tokens
            }
        }

    def _build_emotion_prompt(self, analysis: EmotionAnalysis, context: str) -> str:
        template = self.prompt_templates['es']['emotion']
        return template.format(
            num=self._max_suggestions,
            emotion=analysis.predominant_emotion.value,
            confidence=analysis.confidence,
            context=context
        )

    def _build_text_prompt(self, text: str, context: str, language: str) -> str:
        template = self.prompt_templates.get(language, self.prompt_templates['es'])['text']
        return template.format(
            num=self._max_suggestions,
            text=text[:500],  # Limitar texto para evitar sobrecarga
            context=context
        )

    def _call_openai_api(self, prompt: str) -> str:
        self._request_count += 1
        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": "Eres un asistente especializado en servicio al cliente"},
                {"role": "user", "content": prompt}
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            n=1
        )
        return response.choices[0].message.content

    def _parse_suggestions(self, raw_text: str, target_emotion: Optional[EmotionType]) -> List[Suggestion]:
        suggestions = []
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        for line in lines:
            try:
                suggestion_type, text = self._parse_line(line)
                suggestions.append(Suggestion(
                    text=text,
                    suggestion_type=suggestion_type,
                    target_emotion=target_emotion or EmotionType.UNIDENTIFIED,
                    confidence=self._creativity,
                    metadata={
                        'source': 'OpenAI',
                        'model': self.default_model
                    }
                ))
            except (ValueError, IndexError):
                continue
                
        return self._apply_business_rules(suggestions)

    def _parse_line(self, line: str) -> tuple[SuggestionType, str]:
        line = line.strip('•-* ')
        if ']' in line:
            type_part, text_part = line.split(']', 1)
            suggestion_type = type_part.strip(' []').upper()
            return (SuggestionType[suggestion_type], text_part.strip())
        return (SuggestionType.STANDARD, line)

    def _parse_context(self, context: Optional[Dict]) -> str:
        if not context:
            return "sin contexto adicional"
        return ", ".join(f"{k}: {v}" for k, v in context.items())