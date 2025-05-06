# core/use_cases/manage_history_use_case.py
from core.entities.conversation_history import ConversationHistory

class ManageHistoryUseCase:
    def __init__(self, history_repository):
        self.history_repository = history_repository

    def start_new_call(self, client_id):
        history = self.history_repository.get_or_create_history(client_id)
        return history.start_new_call()

    def add_transcription(self, client_id, call_name, text):
        history = self.history_repository.get_or_create_history(client_id)
        history.add_transcription(call_name, text)

    def add_emotion(self, client_id, call_name, emotion, score=1.0):
        history = self.history_repository.get_or_create_history(client_id)
        history.add_emotion(call_name, emotion, score)

    def add_suggestion(self, client_id, call_name, suggestion): # Mantener si aún se usa
        history = self.history_repository.get_or_create_history(client_id)
        history.add_suggestion(call_name, suggestion)

    def add_ranked_suggestion(self, client_id, call_name, ranked_data): # <--- NUEVO MÉTODO
        history = self.history_repository.get_or_create_history(client_id)
        history.add_ranked_suggestion(call_name, ranked_data) # Llama al método de la entidad

    def get_client_history(self, client_id):
        return self.history_repository.get_history(client_id)