from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class BrowserTab(QWebEngineView):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.setUrl(QUrl(url))
