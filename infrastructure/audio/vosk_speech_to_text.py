import wave
import io
import json
from vosk import Model, KaldiRecognizer

class VoskSpeechToText:
    def __init__(self):
        self.model = Model("models/vosk/es")

    def transcribe(self, audio_bytes):
        try:
            # ✅ Crear un archivo WAV válido en memoria
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)

            buffer.seek(0)  # Volver al inicio del buffer

            wf = wave.open(buffer, "rb")
            rec = KaldiRecognizer(self.model, wf.getframerate())

            text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text += result.get("text", "") + " "

            final_result = json.loads(rec.FinalResult())
            final_text = (text + final_result.get("text", "")).strip()

            print("📄 Texto reconocido por Vosk:", final_text)
            return final_text

        except Exception as e:
            print("❌ Error en transcripción:", e)
            return ""
