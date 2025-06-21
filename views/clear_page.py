# 全データ削除を実行するページ

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class ClearPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("登録データを全て削除"))
        self.run_button = QPushButton("全削除 実行")
        layout.addWidget(self.run_button)
        layout.addStretch()
