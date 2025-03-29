from abc import ABC, abstractmethod
from typing import Generator

class AudioInterface(ABC):
    
    @abstractmethod
    def start_recording(self) -> None:
        pass
    
    @abstractmethod
    def stop_recording(self) -> None:
        pass

    @abstractmethod
    def get_audio_stream(self) -> Generator[bytes, None, None]:
        pass

    @abstractmethod
    def get_full_recording(self) -> bytes:
        pass
