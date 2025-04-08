class TranscriptionUseCase:
    def __init__(self, speech_to_text):
        self.speech_to_text = speech_to_text


    def run(self, audio_chunk):
        """
        Procesa un bloque de audio y retorna las nuevas palabras detectadas.
        """
        if self.speech_to_text.accept_waveform(audio_chunk):
            result = self.speech_to_text.get_result()
            return result.get("text", "")
        else:
            partial = self.speech_to_text.get_partial()
            return partial.get("partial", "")
