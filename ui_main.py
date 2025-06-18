from PySide6.QtWidgets import (
    QMainWindow, QWidget, QListWidget, QStackedWidget, QTableView,
    QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
)
from controller import Controller
from PySide6.QtCore import Qt
from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日本郵便住所データ管理")
        self.resize(1000, 700)

        self.controller = Controller()

        # サイドメニュー
        self.menu = QListWidget()
        self.menu.addItems(["一括登録", "差分追加", "差分削除", "検索"])
        self.menu.setFixedWidth(180)
        self.menu.currentRowChanged.connect(self.switch_page)

        # ページ切替部
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_page(
            "一括登録", "一括登録 実行", self.run_bulk))
        self.stack.addWidget(self.create_page("差分追加", "差分追加 実行", self.run_add))
        self.stack.addWidget(self.create_page("差分削除", "差分削除 実行", self.run_del))
        self.stack.addWidget(self.create_search_page())

        # メイン領域
        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.addWidget(self.menu)
        hbox.addWidget(self.stack, 1)

        # 出力ログ欄
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(150)

        # 全体レイアウト
        layout = QVBoxLayout()
        layout.addWidget(container)
        layout.addWidget(QLabel("■ 出力ログ"))
        layout.addWidget(self.output)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.menu.setCurrentRow(0)

    def create_page(self, label_text, btn_text, slot):
        page = QWidget()
        v = QVBoxLayout(page)
        v.addWidget(QLabel(label_text + "用 URL"))
        url_input = QLineEdit()
        setattr(self, label_text.replace("一括登録", "url_all")
                .replace("差分追加", "url_add")
                .replace("差分削除", "url_del"), url_input)
        btn = QPushButton(btn_text)
        btn.clicked.connect(lambda: self.run_bulk(self.url_all.text()))
        v.addWidget(url_input)
        v.addWidget(btn)
        v.addStretch()
        return page

    def create_search_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.addWidget(QLabel("検索"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("郵便番号・市区町村・町域 等で検索")
        v.addWidget(self.search_input)

        self.table = QTableView()
        v.addWidget(self.table, 1)

        # モデルとフィルタ設定
        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(["郵便番号", "都道府県", "市区町村", "町域"])
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1)  # 全列検索
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table.setModel(self.proxy)

        self.search_input.textChanged.connect(self.proxy.setFilterFixedString)
        return page

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 3:  # 検索ページならデータ読み込み
            self.load_table_data()

    def load_table_data(self):
        data = self.controller.get_all_addresses()
        self.model.removeRows(0, self.model.rowCount())
        for zipcode, pref, city, town in data:
            items = [QStandardItem(x) for x in [zipcode, pref, city, town]]
            for item in items:
                item.setEditable(False)
            self.model.appendRow(items)

    def run_bulk(self, url):
        msg = self.controller.bulk_register(url)
        self.output.append(msg)

    def run_add(self, url):
        msg = self.controller.apply_add(url)
        self.output.append(msg)

    def run_del(self, url):
        msg = self.controller.apply_del(url)
        self.output.append(msg)
