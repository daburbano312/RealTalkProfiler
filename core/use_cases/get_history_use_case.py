class GetHistoryUseCase:
    def __init__(self, history_repository):
        self.history_repository = history_repository

    def get_client_history(self, client_id):
        return self.history_repository.get_history(client_id)
