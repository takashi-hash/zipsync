from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt


class JsonDataPage(QWidget):
    """Import and export JSON data."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("データの保存・復元")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        info = QLabel(
            "住所データや履歴のJSONバックアップとインポートを行います。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: gray;")
        layout.addWidget(info)

        import_row = QHBoxLayout()
        import_label = QLabel("データをインポート")
        self.import_btn = QPushButton("インポート")
        self.import_btn.setObjectName("primaryButton")
        self.import_btn.setFixedHeight(40)
        self.import_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        import_row.addWidget(import_label)
        import_row.addWidget(self.import_btn)
        import_row.addStretch()
        layout.addLayout(import_row)

        export_row = QHBoxLayout()
        export_label = QLabel("データをエクスポート")
        self.export_btn = QPushButton("エクスポート")
        self.export_btn.setObjectName("primaryButton")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        export_row.addWidget(export_label)
        export_row.addWidget(self.export_btn)
        export_row.addStretch()
        layout.addLayout(export_row)

        layout.addStretch()

