from infrastructure.audio.audio_recorder import PyAudioRecorder
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from core.entities.transcription import Transcription
from core.use_cases.emotion_analysis import EmotionAnalysisUseCase
from datetime import datetime

class AudioProcessingUseCase:
    def __init__(self):
        self.recorder = PyAudioRecorder()
        self.stt_service = VoskSpeechToText()
        self.emotion_analysis_use_case = EmotionAnalysisUseCase()

    def process_audio(self) -> Transcription:
        self.recorder.start_recording()
        print("Grabando audio... Presiona Enter para detener.")
        input()
        self.recorder.stop_recording()

        audio_data = self.recorder.get_full_recording()
        text = self.stt_service.transcribe(audio_data)
        emotion_analysis = self.emotion_analysis_use_case.analyze_audio_and_text(audio_data, text)

        transcription = Transcription(
            text=text,
            emotion_analysis=emotion_analysis,
            audio_duration=len(audio_data) / (self.recorder.rate * 2),
            timestamp=datetime.now()
        )
        return transcription
