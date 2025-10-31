import json
import os

class HistoryManager:
    def __init__(self, file_path="history.json"):
        self.file_path = file_path
        self.history = self.load()

    def add(self, url):
        if url not in self.history:
            self.history.append(url)
            self.save()

    def get_history(self):
        return self.history

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.history, f)

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return []

class FavoritesManager:
    def __init__(self, file_path="favorites.json"):
        self.file_path = file_path
        self.favorites = self.load()

    def add(self, url):
        if url not in self.favorites:
            self.favorites.append(url)
            self.save()

    def remove(self, url):
        if url in self.favorites:
            self.favorites.remove(url)
            self.save()

    def get_all(self):
        return self.favorites

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.favorites, f)

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return []
