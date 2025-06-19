from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTableView, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("差分取込履歴"))

        self.model = QStandardItemModel(0, 5)
        self.model.setHorizontalHeaderLabels([
            "選択", "種別", "ファイル", "件数", "日時"
        ])
        self.table = QTableView()
        self.table.setModel(self.model)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(4, 150)
        self.table.doubleClicked.connect(self._show_details)
        layout.addWidget(self.table, 1)

        self.logs = []

        actions = QHBoxLayout()
        self.restore_btn = QPushButton("復元")
        self.delete_log_btn = QPushButton("履歴削除")
        for w in [self.restore_btn, self.delete_log_btn]:
            actions.addWidget(w)
        actions.addStretch()
        layout.addLayout(actions)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.page_label = QLabel("1 / 1")
        self.next_btn = QPushButton("次へ")
        for w in [self.prev_btn, self.page_label, self.next_btn]:
            pager.addWidget(w)
        pager.addStretch()
        layout.addLayout(pager)

        self.current_page = 1
        self.total_pages = 1

    def _show_details(self, index):
        row = index.row()
        if row >= len(self.logs):
            return
        log = self.logs[row]
        details = log.get("details", [])
        detail_lines = [f"{d.get('zipcode', '')} {d.get('pref', '')} {d.get('town', '')}" for d in details]
        text = "\n".join(detail_lines) if detail_lines else "(詳細なし)"
        QMessageBox.information(self, "詳細", text)
