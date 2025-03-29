from abc import ABC, abstractmethod

class SpeechToTextInterface(ABC):

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        pass
