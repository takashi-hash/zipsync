# 詳細検索を行うページ

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit,
    QPushButton, QTableView, QAbstractItemView
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QStandardItemModel, QStandardItem, QRegularExpressionValidator


class SearchPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("詳細検索")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.form_container = QVBoxLayout()
        layout.addLayout(self.form_container)

        self.rows = []

        add_row_area = QHBoxLayout()
        self.add_row_btn = QPushButton("＋ 条件追加")
        self.add_row_btn.setObjectName("secondaryButton")
        self.add_row_btn.clicked.connect(self._add_row)
        add_row_area.addWidget(self.add_row_btn)
        add_row_area.addStretch()
        layout.addLayout(add_row_area)

        self._add_row()
        self._update_add_button()

        self.search_btn = QPushButton("検索")
        self.search_btn.setObjectName("primaryButton")
        layout.addWidget(self.search_btn)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.table, 1)

        self.add_custom_btn = QPushButton("項目を追加")
        self.add_custom_btn.setObjectName("primaryButton")
        self.add_custom_btn.setEnabled(False)
        layout.addWidget(self.add_custom_btn)

        self.no_results_label = QLabel("")
        layout.addWidget(self.no_results_label)

        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(["郵便番号", "都道府県", "市区町村", "町域"])
        self.table.setModel(self.model)
        self.table.selectionModel().selectionChanged.connect(self._update_button_state)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.prev_btn.setObjectName("secondaryButton")
        self.next_btn = QPushButton("次へ")
        self.next_btn.setObjectName("secondaryButton")
        self.page_label = QLabel("1 / 1")
        for w in [self.prev_btn, self.page_label, self.next_btn]:
            pager.addWidget(w)
        pager.addStretch()
        layout.addLayout(pager)

        self.current_page = 1
        self.total_pages = 1

    def _create_row(self):
        row = {}
        layout = QHBoxLayout()
        row["layout"] = layout
        row["zip"] = QLineEdit()
        row["zip"].setPlaceholderText("郵便番号")
        row["zip"].setMaxLength(7)
        regex = QRegularExpression(r"\d{0,7}")
        row["zip"].setValidator(QRegularExpressionValidator(regex))
        row["pref"] = QLineEdit()
        row["pref"].setPlaceholderText("都道府県")
        row["city"] = QLineEdit()
        row["city"].setPlaceholderText("市区町村")
        row["town"] = QLineEdit()
        row["town"].setPlaceholderText("町域")
        row["remove"] = QPushButton("－")
        row["remove"].setObjectName("dangerButton")
        row["remove"].clicked.connect(lambda: self._remove_row(row))
        for w in [row["zip"], row["pref"], row["city"], row["town"], row["remove"]]:
            layout.addWidget(w)
        return row

    def _add_row(self):
        if len(self.rows) >= 4:
            return
        row = self._create_row()
        self.rows.append(row)
        self.form_container.addLayout(row["layout"])
        self._update_remove_buttons()
        self._update_add_button()

    def _remove_row(self, row):
        if row not in self.rows:
            return
        self.rows.remove(row)
        while row["layout"].count():
            item = row["layout"].takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.form_container.removeItem(row["layout"])
        self._update_remove_buttons()
        self._update_add_button()

    def _update_remove_buttons(self):
        enable = len(self.rows) > 1
        for r in self.rows:
            r["remove"].setEnabled(enable)

    def _update_add_button(self):
        self.add_row_btn.setEnabled(len(self.rows) < 4)

    def get_filters(self):
        filters = []
        for r in self.rows:
            data = {
                "zipcode": r["zip"].text().strip(),
                "pref": r["pref"].text().strip(),
                "city": r["city"].text().strip(),
                "town": r["town"].text().strip(),
            }
            if any(data.values()):
                filters.append(data)
        if not filters:
            filters.append({"zipcode": "", "pref": "", "city": "", "town": ""})
        return filters

    def _update_button_state(self, *args):
        selected = bool(self.table.selectionModel().selectedRows())
        self.add_custom_btn.setEnabled(selected)

    def selected_zipcodes(self):
        zips = []
        for index in self.table.selectionModel().selectedRows():
            zips.append(self.model.item(index.row(), 0).text())
        return zips
