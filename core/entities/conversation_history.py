class ConversationHistory:
    def __init__(self, client_id):
        self.client_id = client_id
        self.calls = {}  # Cada llamada tendrá un nombre: Llamada 1, Llamada 2, etc.

    def start_new_call(self):
        call_number = len(self.calls) + 1
        call_name = f"Llamada {call_number}"
        self.calls[call_name] = {
            "transcriptions": [],
            "emotions": [],
            "suggestions": []
        }
        return call_name

    def add_transcription(self, call_name, text):
        self.calls[call_name]["transcriptions"].append(text)

    def add_emotion(self, call_name, emotion, score=1.0):
        self.calls[call_name]["emotions"].append({"emotion": emotion, "score": score})

    def add_suggestion(self, call_name, suggestion):
        self.calls[call_name]["suggestions"].append(suggestion)

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "calls": self.calls
        }
