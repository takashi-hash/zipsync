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

        self.no_results_label = QLabel("")
        layout.addWidget(self.no_results_label)

        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(["郵便番号", "都道府県", "市区町村", "町域"])
        self.table.setModel(self.model)

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
