# core/entities/conversation_history.py
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
            "suggestions": [], # Puedes mantener la sugerencia original o eliminarla
            "ranked_suggestions": [] # <--- NUEVO CAMPO
        }
        return call_name

    def add_transcription(self, call_name, text):
        if call_name in self.calls:
            self.calls[call_name]["transcriptions"].append(text)

    def add_emotion(self, call_name, emotion, score=1.0):
        if call_name in self.calls:
            self.calls[call_name]["emotions"].append({"emotion": emotion, "score": score})

    def add_suggestion(self, call_name, suggestion):
        if call_name in self.calls:
            self.calls[call_name]["suggestions"].append(suggestion) # Mantener si aún se usa

    def add_ranked_suggestion(self, call_name, ranked_data): # <--- NUEVO MÉTODO
        """ Añade los datos del ranking (el diccionario/JSON parseado) """
        if call_name in self.calls:
             # Guardamos el diccionario completo recibido de la IA
            self.calls[call_name]["ranked_suggestions"].append(ranked_data)

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "calls": self.calls # Ahora incluye 'ranked_suggestions' dentro de cada call
        }