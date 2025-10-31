import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt6.QtCore import QUrl
from browser_tab import BrowserTab
from navbar import NavBar
from utils import HistoryManager, FavoritesManager

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")
        self.resize(1200, 800)

        # 履歴・お気に入り管理
        self.history_manager = HistoryManager()
        self.favorites_manager = FavoritesManager()

        # タブ
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # ツールバー
        self.navbar = NavBar(self, self.history_manager, self.favorites_manager)
        self.addToolBar(self.navbar)

        # 最初のタブ
        self.add_tab()

        # スタイル適用
        self.load_styles("styles.qss")

    def load_styles(self, file_path):
        with open(file_path, "r") as f:
            self.setStyleSheet(f.read())

    # タブ関連
    def add_tab(self, url="https://www.google.com"):
        new_tab = BrowserTab(url)
        index = self.tabs.addTab(new_tab, "新しいタブ")
        self.tabs.setCurrentIndex(index)
        new_tab.urlChanged.connect(lambda qurl, browser=new_tab: self.update_tab_title(browser))
        new_tab.urlChanged.connect(lambda qurl, browser=new_tab: self.history_manager.add(qurl.toString()))
        self.update_url_bar(index)

    def update_tab_title(self, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, browser.title())

    def update_url_bar(self, index):
        browser = self.tabs.currentWidget()
        if browser:
            self.navbar.url_bar.setText(browser.url().toString())

    # ナビゲーション
    def navigate_to_url(self, url=None):
        browser = self.tabs.currentWidget()
        if browser:
            if not url:
                url = self.navbar.url_bar.text()
            if not url.startswith("http"):
                url = "http://" + url
            browser.setUrl(QUrl(url))

    def back(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.back()

    def forward(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.forward()

    def reload(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())

from PyQt6.QtWidgets import QMenu

# タブ右クリック
self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
self.tabs.customContextMenuRequested.connect(self.tab_context_menu)

def tab_context_menu(self, pos):
    index = self.tabs.tabBar().tabAt(pos)
    if index == -1:
        return
    menu = QMenu()
    close_action = menu.addAction("閉じる")
    duplicate_action = menu.addAction("複製")
    action = menu.exec(self.tabs.mapToGlobal(pos))
    if action == close_action:
        self.tabs.removeTab(index)
    elif action == duplicate_action:
        browser = self.tabs.widget(index)
        self.add_tab(browser.url().toString())
