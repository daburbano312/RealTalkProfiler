import pyaudio

class PyAudioRecorder:
    def __init__(self, rate=48000, chunk=1024, record_seconds=4):
        self.rate = rate
        self.chunk = chunk
        self.record_seconds = record_seconds
        self.audio = pyaudio.PyAudio()
        self.device_index = 9  # Índice del micrófono válido
        self.stream = None

    def get_full_recording(self) -> bytes:
        print("[INFO] Grabando audio... Presiona Enter para detener (o espera tiempo automático).")

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk
        )

        frames = []

        try:
            for _ in range(0, int(self.rate / self.chunk * self.record_seconds)):
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
        except Exception as e:
            print(f"[ERROR] Error al grabar audio: {e}")

        self.stream.stop_stream()
        self.stream.close()

        return b''.join(frames)

    def terminate(self):
        self.audio.terminate()

    def start_recording(self):
        # Método opcional para evitar errores si es llamado
        pass

    def stop_recording(self):
        # Método opcional para evitar errores si es llamado
        pass
