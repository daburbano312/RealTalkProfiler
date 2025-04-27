from core.entities.conversation_history import ConversationHistory

class HistoryRepository:
    def __init__(self):
        self.histories = {}

    def get_or_create_history(self, client_id):
        if client_id not in self.histories:
            self.histories[client_id] = ConversationHistory(client_id)
        return self.histories[client_id]

    def get_history(self, client_id):
        return self.histories.get(client_id)
