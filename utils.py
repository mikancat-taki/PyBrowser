# 履歴管理とお気に入り機能

class HistoryManager:
    def __init__(self):
        self.history = []

    def add(self, url):
        if url not in self.history:
            self.history.append(url)

    def get_history(self):
        return self.history

class FavoritesManager:
    def __init__(self):
        self.favorites = []

    def add(self, url):
        if url not in self.favorites:
            self.favorites.append(url)

    def remove(self, url):
        if url in self.favorites:
            self.favorites.remove(url)

    def get_all(self):
        return self.favorites
