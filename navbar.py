from PyQt6.QtWidgets import QToolBar, QLineEdit, QAction

class NavBar(QToolBar):
    def __init__(self, parent_browser):
        super().__init__()
        self.browser_window = parent_browser

        # 戻る
        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.browser_window.back)
        self.addAction(back_btn)

        # 進む
        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.browser_window.forward)
        self.addAction(forward_btn)

        # 更新
        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.browser_window.reload)
        self.addAction(reload_btn)

        # URLバー
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.browser_window.navigate_to_url)
        self.addWidget(self.url_bar)

        # 新しいタブ
        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(self.browser_window.add_tab)
        self.addAction(new_tab_btn)
