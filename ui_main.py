import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QListWidget, QStackedWidget, QTextEdit, QLabel,
    QHBoxLayout, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from controller import Controller
from views.register_page import RegisterPage
from views.clear_page import ClearPage
from views.search_page import SearchPage
from views.logs_page import LogsPage


class EmittingStream(QObject):
    """Redirect writes to a Qt signal."""
    text_written = Signal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日本郵便住所データ管理")
        self.resize(1000, 700)

        self.controller = Controller()

        # サイドメニュー
        self.menu = QListWidget()
        self.menu.addItems(["一括登録", "差分追加", "差分削除", "全削除", "検索", "履歴"])
        self.menu.setFixedWidth(180)
        self.menu.currentRowChanged.connect(self.switch_page)

        # 各ページを作成
        self.bulk_page = RegisterPage("一括登録", "一括登録 実行")
        self.add_page = RegisterPage("差分追加", "差分追加 実行")
        self.del_page = RegisterPage("差分削除", "差分削除 実行")
        self.clear_page = ClearPage()
        self.search_page = SearchPage()
        self.logs_page = LogsPage()

        # ボタンに処理を接続
        self.bulk_page.run_button.clicked.connect(
            lambda: self.run_bulk(self.bulk_page.url_input.text()))
        self.add_page.run_button.clicked.connect(
            lambda: self.run_add(self.add_page.url_input.text()))
        self.del_page.run_button.clicked.connect(
            lambda: self.run_del(self.del_page.url_input.text()))
        self.clear_page.run_button.clicked.connect(self.run_clear)
        self.search_page.search_btn.clicked.connect(lambda: self.perform_search(1))
        self.search_page.prev_btn.clicked.connect(self.prev_page)
        self.search_page.next_btn.clicked.connect(self.next_page)
        self.logs_page.restore_btn.clicked.connect(self.restore_selected_logs)
        self.logs_page.delete_log_btn.clicked.connect(self.delete_selected_logs)
        self.logs_page.prev_btn.clicked.connect(
            lambda: self.load_logs_page(self.log_current_page - 1))
        self.logs_page.next_btn.clicked.connect(
            lambda: self.load_logs_page(self.log_current_page + 1))

        # ページ切替部
        self.stack = QStackedWidget()
        for page in [self.bulk_page, self.add_page, self.del_page,
                     self.clear_page, self.search_page, self.logs_page]:
            self.stack.addWidget(page)

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

        # --- コンソール出力をGUIへリダイレクト ---
        self._stream = EmittingStream()
        self._stream.text_written.connect(self._append_output)
        sys.stdout = self._stream
        sys.stderr = self._stream

        self.menu.setCurrentRow(0)

    def _append_output(self, text: str):
        if text.strip():
            self.output.append(text.rstrip())



    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 4:  # 検索ページ
            self.perform_search(1)
        elif index == 5:  # 履歴ページ
            self.load_logs_page(1)

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
        if self.controller.get_record_count() > 0:
            reply = QMessageBox.question(
                self,
                "確認",
                "既にデータが存在します。削除して一括登録しますか？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                self.output.append("[CANCELLED] 一括登録を中止しました")
                return
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
        zipcode = self.search_page.zip_input.text().strip()
        pref = self.search_page.pref_input.text().strip()
        city = self.search_page.city_input.text().strip()
        town = self.search_page.town_input.text().strip()
        records, total = self.controller.search_addresses(
            zipcode, pref, city, town, page, per_page=30)

        self.search_page.model.removeRows(0, self.search_page.model.rowCount())
        for zipcode, pref, city, town in records:
            items = [QStandardItem(x) for x in [zipcode, pref, city, town]]
            for item in items:
                item.setEditable(False)
            self.search_page.model.appendRow(items)

        if total == 0:
            self.search_page.no_results_label.setText("検索結果は0件です")
        else:
            self.search_page.no_results_label.setText("")

        self.current_page = page
        self.total_pages = max(1, (total + 29) // 30)
        self.search_page.page_label.setText(
            f"{self.current_page} / {self.total_pages}")
        self.search_page.prev_btn.setEnabled(self.current_page > 1)
        self.search_page.next_btn.setEnabled(self.current_page < self.total_pages)

    def prev_page(self):
        if self.current_page > 1:
            self.perform_search(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.perform_search(self.current_page + 1)

    # --- log page related ---
    def load_logs_page(self, page: int = 1):
        logs, total = self.controller.fetch_logs(page, per_page=30)

        self.logs_page.model.removeRows(0, self.logs_page.model.rowCount())
        for log in logs:
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setData(log["index"], Qt.UserRole)
            type_item = QStandardItem("追加" if log["type"] == "add" else "削除")
            file_item = QStandardItem(log.get("source_file", ""))
            count_item = QStandardItem(str(log.get("record_count", 0)))
            ts_item = QStandardItem(log.get("timestamp", ""))
            for item in [check_item, type_item, file_item, count_item, ts_item]:
                item.setEditable(False)
            self.logs_page.model.appendRow([check_item, type_item, file_item, count_item, ts_item])

        self.log_current_page = page
        self.log_total_pages = max(1, (total + 29) // 30)
        self.logs_page.page_label.setText(f"{self.log_current_page} / {self.log_total_pages}")
        self.logs_page.prev_btn.setEnabled(self.log_current_page > 1)
        self.logs_page.next_btn.setEnabled(self.log_current_page < self.log_total_pages)

    def _selected_log_indices(self):
        indices = []
        for row in range(self.logs_page.model.rowCount()):
            item = self.logs_page.model.item(row, 0)
            if item.checkState() == Qt.Checked:
                idx = item.data(Qt.UserRole)
                indices.append(idx)
        return indices

    def restore_selected_logs(self):
        indices = self._selected_log_indices()
        if not indices:
            return
        msg = self.controller.reverse_logs(indices)
        self.output.append(msg)
        self.load_logs_page(self.log_current_page)

    def delete_selected_logs(self):
        indices = self._selected_log_indices()
        if not indices:
            return
        msg = self.controller.delete_logs(indices)
        self.output.append(msg)
        self.load_logs_page(self.log_current_page)
