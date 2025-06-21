# 全データ削除を実行するページ

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt


class ClearPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("登録データを全て削除")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        self.run_button = QPushButton("全削除 実行")
        self.run_button.setObjectName("dangerButton")
        self.run_button.setFixedHeight(40)
        self.run_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.run_button, alignment=Qt.AlignCenter)
        layout.addStretch()
