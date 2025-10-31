import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import QFile
from browser_tab import BrowserTab
from navbar import NavBar

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")
        self.resize(1200, 800)

        # タブ
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # ツールバー
        self.navbar = NavBar(self)
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
    def navigate_to_url(self):
        url = self.navbar.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(url)

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
