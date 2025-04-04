from vosk import Model, KaldiRecognizer
import json

class VoskSpeechToText:
    def __init__(self, model_path="models/vosk/es"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def accept_waveform(self, audio_chunk):
        return self.recognizer.AcceptWaveform(audio_chunk)

    def get_result(self):
        return json.loads(self.recognizer.Result())

    def get_partial(self):
        return json.loads(self.recognizer.PartialResult())
