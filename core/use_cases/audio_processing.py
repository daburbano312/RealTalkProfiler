from infrastructure.audio.audio_recorder import PyAudioRecorder
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from core.entities.transcription import Transcription
from core.use_cases.emotion_analysis import EmotionAnalysisUseCase
from datetime import datetime
import threading

class AudioProcessingUseCase:
    def __init__(self):
        self.recorder = PyAudioRecorder()
        self.stt_service = VoskSpeechToText()
        self.emotion_analysis_use_case = EmotionAnalysisUseCase()

    # 🔴 MODO INTERACTIVO (para consola)
    def process_audio(self) -> Transcription:
        print("🎙️ Preparado para grabar...")
        input("🔴 Presiona ENTER para comenzar a grabar...")

        thread = threading.Thread(target=self.recorder.start_recording)
        thread.start()

        input("▶️ Grabando... Presiona ENTER para detener.\n")
        self.recorder.stop_recording()
        print("✅ Stop de grabación ejecutado")

        thread.join()
        print("✅ Hilo finalizado")

        audio_data = self.recorder.get_full_recording()
        print("📦 Bytes de audio grabados:", len(audio_data))

        with open("grabacion.wav", "wb") as f:
            f.write(audio_data)
        print("💾 Audio guardado como 'grabacion.wav'")

        text = self.stt_service.transcribe(audio_data)
        print("📝 Texto transcrito:", text)

        emotion_analysis = self.emotion_analysis_use_case.analyze_audio_and_text(audio_data, text)
        print("📤 Emociones detectadas:", emotion_analysis)

        transcription = Transcription(
            text=text,
            emotion_analysis=emotion_analysis,
            audio_duration=len(audio_data) / (self.recorder.rate * 2),
            timestamp=datetime.now()
        )
        return transcription

    # 🔁 MODO AUTOMÁTICO (para API)
    def process_audio_automatic(self, seconds=6) -> Transcription:
        print(f"🎙️ Grabando automáticamente por {seconds} segundos...")
        self.recorder.record_for(seconds=seconds)

        audio_data = self.recorder.get_full_recording()
        print("📦 Bytes de audio grabados:", len(audio_data))

        with open("grabacion.wav", "wb") as f:
            f.write(audio_data)
        print("💾 Audio guardado como 'grabacion.wav'")

        text = self.stt_service.transcribe(audio_data)
        print("📝 Texto transcrito:", text)

        emotion_analysis = self.emotion_analysis_use_case.analyze_audio_and_text(audio_data, text)
        print("📤 Emociones detectadas:", emotion_analysis)

        transcription = Transcription(
            text=text,
            emotion_analysis=emotion_analysis,
            audio_duration=len(audio_data) / (self.recorder.rate * 2),
            timestamp=datetime.now()
        )
        return transcription
