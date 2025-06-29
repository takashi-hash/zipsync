# 取込履歴を表示するページ

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTableView, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("差分取込履歴")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel(
            "一覧から履歴を選択し、下のボタンで復元・再実行・削除できます。"
        ))

        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels([
            "種別", "ファイル", "件数", "日時"
        ])

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.prev_btn.setObjectName("secondaryButton")
        self.page_label = QLabel("1 / 1")
        self.next_btn = QPushButton("次へ")
        self.next_btn.setObjectName("secondaryButton")
        for w in [self.prev_btn, self.page_label, self.next_btn]:
            pager.addWidget(w)
        pager.addStretch()
        layout.addLayout(pager)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(3, 150)
        self.table.doubleClicked.connect(self._show_details)
        self.table.clicked.connect(self._display_details)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.restore_btn = QPushButton("復元")
        self.restore_btn.setObjectName("primaryButton")
        self.reapply_btn = QPushButton("再実行")
        self.reapply_btn.setObjectName("primaryButton")
        self.delete_log_btn = QPushButton("履歴削除")
        self.delete_log_btn.setObjectName("dangerButton")
        button_width = max(
            self.restore_btn.sizeHint().width(),
            self.reapply_btn.sizeHint().width(),
            self.delete_log_btn.sizeHint().width(),
        )
        for w in [self.restore_btn, self.reapply_btn, self.delete_log_btn]:
            w.setFixedWidth(button_width)
            actions.addWidget(w)
        actions.insertStretch(0)
        actions.addStretch()
        layout.addLayout(actions)

        self.details_model = QStandardItemModel(0, 4)
        self.details_model.setHorizontalHeaderLabels([
            "郵便番号", "都道府県", "市区町村", "町域"
        ])
        self.details_table = QTableView()
        self.details_table.setModel(self.details_model)
        d_header = self.details_table.horizontalHeader()
        d_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.details_table, 1)

        self.logs = []

        self.current_page = 1
        self.total_pages = 1

    def _show_details(self, index):
        row = index.row()
        if row >= len(self.logs):
            return
        log = self.logs[row]
        details = log.get("details", [])
        detail_lines = [
            f"{d.get('zipcode', '')} {d.get('pref', '')} {d.get('city', '')} {d.get('town', '')}"
            for d in details
        ]
        text = "\n".join(detail_lines) if detail_lines else "(詳細なし)"
        QMessageBox.information(self, "詳細", text)

    def _display_details(self, index):
        row = index.row()
        if row >= len(self.logs):
            return
        self.details_model.removeRows(0, self.details_model.rowCount())
        details = self.logs[row].get("details", [])
        for d in details:
            items = [
                QStandardItem(d.get("zipcode", "")),
                QStandardItem(d.get("pref", "")),
                QStandardItem(d.get("city", "")),
                QStandardItem(d.get("town", "")),
            ]
            for item in items:
                item.setEditable(False)
            self.details_model.appendRow(items)

