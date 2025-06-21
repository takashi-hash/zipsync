# URL を入力して処理を実行するページ

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PySide6.QtGui import QFont, QIcon


class RegisterPage(QWidget):
    """住所データ処理を行う汎用ページ"""
    """Generic page for executing address data operations."""

    def __init__(self, label: str, button_label: str, instructions: str = "", icon_name: str = "system-run"):
        super().__init__()

        self.url_input = QLineEdit()

        layout = QVBoxLayout(self)

        title = QLabel(f"{label}用 URL")
        title_font = QFont()
        title_font.setPointSize(title.font().pointSize() + 2)
        title.setFont(title_font)
        layout.addWidget(title)

        input_font = QFont()
        input_font.setPointSize(self.url_input.font().pointSize() + 2)
        self.url_input.setFont(input_font)
        self.url_input.setFixedHeight(36)
        layout.addWidget(self.url_input)

        self.run_button = QPushButton(button_label)
        self.run_button.setIcon(QIcon.fromTheme(icon_name))
        self.run_button.setFont(input_font)
        self.run_button.setFixedHeight(40)
        layout.addWidget(self.run_button)

        layout.addStretch()

        if instructions:
            info = QLabel(instructions)
            info.setWordWrap(True)
            info.setStyleSheet("color: gray;")
            layout.addWidget(info)
