from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit,
    QPushButton, QTableView
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QStandardItemModel, QStandardItem, QRegularExpressionValidator


class SearchPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("詳細検索"))

        form = QHBoxLayout()
        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText("郵便番号")
        self.zip_input.setMaxLength(7)
        regex = QRegularExpression(r"\d{0,7}")
        self.zip_input.setValidator(QRegularExpressionValidator(regex))
        self.pref_input = QLineEdit()
        self.pref_input.setPlaceholderText("都道府県")
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("市区町村")
        self.town_input = QLineEdit()
        self.town_input.setPlaceholderText("町域")
        self.search_btn = QPushButton("検索")

        for w in [self.zip_input, self.pref_input, self.city_input,
                  self.town_input, self.search_btn]:
            form.addWidget(w)
        layout.addLayout(form)

        self.table = QTableView()
        layout.addWidget(self.table, 1)

        self.add_custom_btn = QPushButton("項目を追加")
        self.add_custom_btn.setEnabled(False)
        layout.addWidget(self.add_custom_btn)

        self.no_results_label = QLabel("")
        layout.addWidget(self.no_results_label)

        self.model = QStandardItemModel(0, 5)
        self.model.setHorizontalHeaderLabels(["選択", "郵便番号", "都道府県", "市区町村", "町域"])
        self.table.setModel(self.model)
        self.model.itemChanged.connect(self._update_button_state)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.next_btn = QPushButton("次へ")
        self.page_label = QLabel("1 / 1")
        for w in [self.prev_btn, self.page_label, self.next_btn]:
            pager.addWidget(w)
        pager.addStretch()
        layout.addLayout(pager)

        self.current_page = 1
        self.total_pages = 1

    def _update_button_state(self, *args):
        selected = False
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.Checked:
                selected = True
                break
        self.add_custom_btn.setEnabled(selected)

    def selected_zipcodes(self):
        zips = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.Checked:
                zips.append(self.model.item(row, 1).text())
        return zips
