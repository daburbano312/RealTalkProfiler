import pyaudio
import threading
import time

class PyAudioRecorder:
    def __init__(self):
        self.rate = 16000  # Frecuencia de muestreo
        self.channels = 1  # Mono
        self.format = pyaudio.paInt16  # 16-bit
        self.chunk = 1024  # Tamaño de cada bloque

        self.audio_interface = pyaudio.PyAudio()
        self.frames = []          # Lista para guardar los bloques de audio
        self.stream = None        # El stream del micrófono
        self.recording = False    # Bandera de grabación

    def _record_loop(self):
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print("❌ Error durante la grabación:", e)
                break

    def record_for(self, seconds=6):
        print(f"[INFO] Grabando audio automáticamente durante {seconds} segundos...")
        self.frames = []

        self.stream = self.audio_interface.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        self.recording = True
        thread = threading.Thread(target=self._record_loop)
        thread.start()

        time.sleep(seconds)

        self.recording = False
        thread.join()

        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

        print("[INFO] Grabación automática finalizada.")

    def get_full_recording(self):
        return b"".join(self.frames)
