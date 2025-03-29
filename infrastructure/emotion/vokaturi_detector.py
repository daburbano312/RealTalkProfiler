from infrastructure.emotion import Vokaturi
from interfaces.emotion_detection.emotion_interface import EmotionDetectionInterface
from core.entities.emotion import EmotionAnalysis, EmotionType
from config.settings import settings
from pathlib import Path
import numpy as np
import ctypes

class VokaturiEmotionDetector(EmotionDetectionInterface):
    def __init__(self):
        dll_path = str(settings.VOKATURI_DLL_PATH)
        if not Path(dll_path).exists():
            raise FileNotFoundError(f"No se encontró la DLL de Vokaturi en: {dll_path}")
        Vokaturi.load(dll_path)

    def analyze_audio(self, audio_data: bytes) -> EmotionAnalysis:
        # Convertimos los bytes a int16
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        if len(audio_array) == 0:
            raise ValueError("El audio recibido está vacío o no se pudo procesar.")

        # Inicializamos Vokaturi Voice
        voice = Vokaturi.Voice(settings.AUDIO_SAMPLE_RATE, len(audio_array), False)

        # Convertimos numpy array a puntero C válido
        c_array = audio_array.ctypes.data_as(ctypes.POINTER(ctypes.c_short))

        # Llenamos el buffer de Vokaturi con el puntero al array
        voice.fill_int16array(len(audio_array), c_array)

        # Analizamos la emoción
        quality = Vokaturi.Quality()
        emotion_probs = Vokaturi.EmotionProbabilities()
        voice.extract(quality, emotion_probs)
        voice.destroy()

        return EmotionAnalysis(
            emotion_type=self._get_predominant_emotion(emotion_probs),
            neutrality_prob=emotion_probs.neutrality,
            happiness_prob=emotion_probs.happiness,
            anger_prob=emotion_probs.anger,
            unidentified_prob=emotion_probs.fear
        )

    def analyze_text(self, text: str) -> EmotionAnalysis:
        raise NotImplementedError("Este detector solo analiza audio.")

    def _get_predominant_emotion(self, probs):
        emotions = {
            EmotionType.NEUTRAL: probs.neutrality,
            EmotionType.HAPPY: probs.happiness,
            EmotionType.ANGRY: probs.anger
        }
        return max(emotions, key=emotions.get)
