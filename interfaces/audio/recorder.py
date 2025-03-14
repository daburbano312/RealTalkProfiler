# interfaces/audio/recorder.py
from abc import ABC, abstractmethod
from typing import Optional, Generator, Union, Tuple
from dataclasses import dataclass
import logging

class RecordingError(Exception):
    """Excepción base para errores de grabación de audio"""
    pass

class DeviceConfigurationError(RecordingError):
    """Error en configuración de dispositivos de audio"""
    pass

@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int = 44100
    channels: int = 1
    format: str = 'float32'
    chunk_size: int = 1024

class AudioRecorder(ABC):
    def __init__(self, format: AudioFormat = AudioFormat()):
        self.format = format
        self._is_recording = False
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def start_recording(self) -> None:
        """Inicia la grabación de audio"""
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        """Detiene la grabación de audio"""
        pass

    @property
    @abstractmethod
    def is_recording(self) -> bool:
        """Indica si la grabación está en curso"""
        pass

    @abstractmethod
    def get_audio_stream(self) -> Generator[bytes, None, None]:
        """Generador que produce chunks de audio en tiempo real"""
        pass

    @abstractmethod
    def get_full_recording(self) -> bytes:
        """Obtiene la grabación completa como un solo buffer"""
        pass

    @abstractmethod
    def list_devices(self) -> Tuple[int, str]:
        """Lista los dispositivos de audio disponibles"""
        pass

    @abstractmethod
    def configure_device(self, device_index: int) -> None:
        """Configura el dispositivo de grabación"""
        pass

    def record_to_file(self, file_path: str) -> None:
        """Grabación directa a archivo (implementación por defecto)"""
        try:
            self.start_recording()
            with open(file_path, 'wb') as f:
                for chunk in self.get_audio_stream():
                    f.write(chunk)
        except Exception as e:
            self.logger.error(f"Error grabando a archivo: {str(e)}")
            raise RecordingError("Error en grabación a archivo") from e
        finally:
            self.stop_recording()