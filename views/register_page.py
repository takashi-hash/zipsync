# URL を入力して処理を実行するページ

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton


class RegisterPage(QWidget):
    """住所データ処理を行う汎用ページ"""
    """Generic page for executing address data operations."""

    def __init__(self, label: str, button_label: str):
        super().__init__()
        self.url_input = QLineEdit()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"{label}用 URL"))
        layout.addWidget(self.url_input)
        self.run_button = QPushButton(button_label)
        layout.addWidget(self.run_button)
        layout.addStretch()
