import pyaudio

class AudioStreamer:
    def __init__(self, callback):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.callback = callback

    def start_stream(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=4000,
                                  stream_callback=self._callback)
        self.stream.start_stream()

    def _callback(self, in_data, frame_count, time_info, status):
        self.callback(in_data)
        return (in_data, pyaudio.paContinue)

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
