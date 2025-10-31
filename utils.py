# 将来的な履歴管理やお気に入り機能用
class HistoryManager:
    def __init__(self):
        self.history = []

    def add(self, url):
        self.history.append(url)

    def get_history(self):
        return self.history
