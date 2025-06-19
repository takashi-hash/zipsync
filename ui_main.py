from PySide6.QtWidgets import (
    QMainWindow, QWidget, QListWidget, QStackedWidget, QTableView,
    QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
)
from controller import Controller
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QRegularExpressionValidator,
    QRegularExpression,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日本郵便住所データ管理")
        self.resize(1000, 700)

        self.controller = Controller()

        # サイドメニュー
        self.menu = QListWidget()
        self.menu.addItems(["一括登録", "差分追加", "差分削除", "全削除", "検索"])
        self.menu.setFixedWidth(180)
        self.menu.currentRowChanged.connect(self.switch_page)

        # ページ切替部
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_page(
            "一括登録", "一括登録 実行", self.run_bulk))
        self.stack.addWidget(self.create_page("差分追加", "差分追加 実行", self.run_add))
        self.stack.addWidget(self.create_page("差分削除", "差分削除 実行", self.run_del))
        self.stack.addWidget(self.create_clear_page())
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
        btn.clicked.connect(lambda: slot(url_input.text()))
        v.addWidget(url_input)
        v.addWidget(btn)
        v.addStretch()
        return page

    def create_clear_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.addWidget(QLabel("登録データを全て削除"))
        btn = QPushButton("全削除 実行")
        btn.clicked.connect(self.run_clear)
        v.addWidget(btn)
        v.addStretch()
        return page

    def create_search_page(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.addWidget(QLabel("詳細検索"))

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
        self.search_btn = QPushButton("検索")
        self.search_btn.clicked.connect(lambda: self.perform_search(1))
        for w in [self.zip_input, self.pref_input, self.city_input, self.search_btn]:
            form.addWidget(w)
        v.addLayout(form)

        self.table = QTableView()
        v.addWidget(self.table, 1)

        self.no_results_label = QLabel("")
        v.addWidget(self.no_results_label)

        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(["郵便番号", "都道府県", "市区町村", "町域"])
        self.table.setModel(self.model)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("次へ")
        self.next_btn.clicked.connect(self.next_page)
        self.page_label = QLabel("1 / 1")
        for w in [self.prev_btn, self.page_label, self.next_btn]:
            pager.addWidget(w)
        pager.addStretch()
        v.addLayout(pager)

        self.current_page = 1
        self.total_pages = 1
        return page

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 4:  # 検索ページならデータ読み込み
            self.perform_search(1)

    def load_table_data(self):
        # 古いAPI互換のため残しているが現在は未使用
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

    def run_clear(self):
        msg = self.controller.clear_database()
        self.output.append(msg)

    # --- 検索関連処理 ---
    def perform_search(self, page: int = 1):
        zipcode = self.zip_input.text().strip()
        pref = self.pref_input.text().strip()
        city = self.city_input.text().strip()
        records, total = self.controller.search_addresses(
            zipcode, pref, city, page, per_page=30)

        self.model.removeRows(0, self.model.rowCount())
        for zipcode, pref, city, town in records:
            items = [QStandardItem(x) for x in [zipcode, pref, city, town]]
            for item in items:
                item.setEditable(False)
            self.model.appendRow(items)

        if total == 0:
            self.no_results_label.setText("検索結果は0件です")
        else:
            self.no_results_label.setText("")

        self.current_page = page
        self.total_pages = max(1, (total + 29) // 30)
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

    def prev_page(self):
        if self.current_page > 1:
            self.perform_search(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.perform_search(self.current_page + 1)
