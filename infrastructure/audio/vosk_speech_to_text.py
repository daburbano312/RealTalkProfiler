from vosk import Model, KaldiRecognizer
import json
from interfaces.audio.speech_to_text_interface import SpeechToTextInterface
from config.settings import settings

class VoskSpeechToText(SpeechToTextInterface):
    def __init__(self):
        self.model = Model(str(settings.VOSK_MODEL_PATH))

    def transcribe(self, audio_data: bytes) -> str:
        recognizer = KaldiRecognizer(self.model, settings.AUDIO_SAMPLE_RATE)
        recognizer.AcceptWaveform(audio_data)
        result = recognizer.Result()
        result_dict = json.loads(result)
        return result_dict.get("text", "")
