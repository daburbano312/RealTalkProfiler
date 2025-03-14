# infrastructure/audio/vokaturi_recorder.py
import Vokaturi
import pyaudio
import numpy as np
from typing import Generator, Tuple, Optional
from interfaces.audio.recorder import AudioRecorder, AudioFormat, RecordingError, DeviceConfigurationError

class VokaturiRecorder(AudioRecorder):
    def __init__(self, format: AudioFormat = AudioFormat(), dll_path: str = ""):
        super().__init__(format)
        self._buffer = Vokaturi.float32array(self.format.chunk_size)
        self._stream = None
        self._audio_data = bytearray()
        self._is_recording = False
        self._load_library(dll_path)
        
    def _load_library(self, dll_path: str):
        try:
            Vokaturi.load(dll_path)
            self._voice = Vokaturi.Voice(
                self.format.sample_rate,
                self.format.chunk_size,
                True
            )
        except Exception as e:
            raise DeviceConfigurationError(f"Error loading Vokaturi library: {str(e)}")

    def start_recording(self) -> None:
        if self._is_recording:
            return
            
        self._audio_data = bytearray()
        self._pa = pyaudio.PyAudio()
        
        try:
            self._stream = self._pa.open(
                rate=self.format.sample_rate,
                channels=self.format.channels,
                format=pyaudio.paFloat32,
                input=True,
                frames_per_buffer=self.format.chunk_size,
                stream_callback=self._callback
            )
            self._is_recording = True
        except Exception as e:
            raise RecordingError(f"Failed to start recording: {str(e)}")

    def stop_recording(self) -> None:
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._pa.terminate()
            self._is_recording = False

    def _callback(self, in_data, frame_count, time_info, status):
        audio_array = np.frombuffer(in_data, dtype=np.float32)
        self._buffer[0:frame_count] = audio_array
        self._voice.fill_float32array(frame_count, self._buffer)
        self._audio_data.extend(in_data)
        return (in_data, pyaudio.paContinue)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def get_audio_stream(self) -> Generator[bytes, None, None]:
        while self._is_recording:
            if len(self._audio_data) >= self.format.chunk_size:
                chunk = bytes(self._audio_data[:self.format.chunk_size])
                self._audio_data = self._audio_data[self.format.chunk_size:]
                yield chunk

    def get_full_recording(self) -> bytes:
        return bytes(self._audio_data)

    def list_devices(self) -> Tuple[int, str]:
        devices = []
        for i in range(self._pa.get_device_count()):
            info = self._pa.get_device_info_by_index(i)
            devices.append((i, info['name']))
        return tuple(devices)

    def configure_device(self, device_index: int) -> None:
        self.stop_recording()
        self.start_recording()