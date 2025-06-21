# アプリケーションメインウィンドウの実装

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QListWidget, QStackedWidget, QTextEdit, QLabel,
    QHBoxLayout, QVBoxLayout, QMessageBox, QToolButton, QFileDialog
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
from views.custom_page import CustomEditPage
from views.json_page import JsonDataPage


class EmittingStream(QObject):
    """print 出力を Qt シグナルへ転送する"""
    text_written = Signal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日本郵便住所データ管理")
        self.resize(1000, 700)

        self.controller = Controller()

        # サイドメニュー
        self.menu_width = 180
        self.menu = QListWidget()
        self.menu.addItems(["一括登録", "差分追加", "差分削除", "全削除", "検索", "履歴", "jsonデータ"])
        self.menu.setFixedWidth(self.menu_width)
        self.menu.currentRowChanged.connect(self.switch_page)

        # サイドバー開閉ボタン
        self.toggle_menu_btn = QToolButton()
        self.toggle_menu_btn.setObjectName("menuToggleButton")
        self.toggle_menu_btn.setArrowType(Qt.LeftArrow)
        self.toggle_menu_btn.setAutoRaise(False)
        self.toggle_menu_btn.clicked.connect(self.toggle_menu)

        self.menu_container = QWidget()
        menu_layout = QVBoxLayout(self.menu_container)
        menu_layout.setContentsMargins(0, 10, 0, 10)
        menu_layout.addWidget(self.toggle_menu_btn, alignment=Qt.AlignRight)
        menu_layout.addWidget(self.menu)

        # 各ページを作成
        bulk_info = (
            "日本郵便サイトの『utf_ken_all.zip』URLを入力し実行してください。\n"
            "既存データは削除され、新しいデータで置き換わります。"
        )
        self.bulk_page = RegisterPage("一括登録", "一括登録 実行", instructions=bulk_info)

        add_info = "日本郵便サイトの『utf_add_YYMM.zip』URLを入力し実行してください。"
        self.add_page = RegisterPage("差分追加", "差分追加 実行", instructions=add_info)

        del_info = "日本郵便サイトの『utf_del_YYMM.zip』URLを入力し実行してください。"
        self.del_page = RegisterPage("差分削除", "差分削除 実行", instructions=del_info)
        self.clear_page = ClearPage()
        self.search_page = SearchPage()
        self.logs_page = LogsPage()
        self.custom_page = CustomEditPage()
        self.json_page = JsonDataPage()
        self._pending_zipcodes = []

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
        self.search_page.add_custom_btn.clicked.connect(self.add_custom_fields)
        self.logs_page.restore_btn.clicked.connect(self.restore_selected_logs)
        self.logs_page.delete_log_btn.clicked.connect(self.delete_selected_logs)
        self.logs_page.reapply_btn.clicked.connect(self.reapply_selected_logs)
        self.logs_page.prev_btn.clicked.connect(
            lambda: self.load_logs_page(self.log_current_page - 1))
        self.logs_page.next_btn.clicked.connect(
            lambda: self.load_logs_page(self.log_current_page + 1))
        self.custom_page.accepted.connect(self._custom_page_accepted)
        self.custom_page.cancelled.connect(self._custom_page_cancelled)
        self.json_page.import_btn.clicked.connect(self.import_json_data)
        self.json_page.export_btn.clicked.connect(self.export_json_data)

        # ページ切替部
        self.stack = QStackedWidget()
        for page in [self.bulk_page, self.add_page, self.del_page,
                     self.clear_page, self.search_page, self.logs_page,
                     self.json_page, self.custom_page]:
            self.stack.addWidget(page)

        # メイン領域
        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.menu_container)
        hbox.addWidget(self.stack, 1)

        # 出力ログ欄
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(150)

        self.toggle_log_btn = QToolButton()
        self.toggle_log_btn.setArrowType(Qt.DownArrow)
        self.toggle_log_btn.setAutoRaise(True)
        self.toggle_log_btn.clicked.connect(self.toggle_log_output)

        log_header = QWidget()
        log_header_layout = QHBoxLayout(log_header)
        log_header_layout.setContentsMargins(0, 0, 0, 0)
        log_header_layout.addWidget(QLabel("■ 出力ログ"))
        log_header_layout.addWidget(self.toggle_log_btn)
        log_header_layout.addStretch()

        # 全体レイアウト
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(container)
        layout.addWidget(log_header)
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

    # --- UI toggle actions ---
    def toggle_menu(self):
        if self.menu.isVisible():
            self.menu.hide()
            self.menu_container.setFixedWidth(self.toggle_menu_btn.sizeHint().width())
            self.toggle_menu_btn.setArrowType(Qt.RightArrow)
        else:
            self.menu.show()
            self.menu_container.setFixedWidth(self.menu_width)
            self.toggle_menu_btn.setArrowType(Qt.LeftArrow)

    def toggle_log_output(self):
        if self.output.isVisible():
            self.output.hide()
            self.toggle_log_btn.setArrowType(Qt.UpArrow)
        else:
            self.output.show()
            self.toggle_log_btn.setArrowType(Qt.DownArrow)



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
        filters = self.search_page.get_filters()
        records, total = self.controller.search_addresses(
            page=page, per_page=30, filters=filters)

        self.search_page.model.removeRows(0, self.search_page.model.rowCount())
        for zipcode, pref, city, town in records:
            row_items = [QStandardItem(x) for x in [zipcode, pref, city, town]]
            for item in row_items:
                item.setEditable(False)
            self.search_page.model.appendRow(row_items)
        self.search_page.table.clearSelection()
        self.search_page._update_button_state()

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

    def add_custom_fields(self):
        selected = self.search_page.selected_zipcodes()
        if not selected:
            return
        records = {}
        for zc in selected:
            rec = self.controller.get_record(zc)
            if rec:
                records[zc] = {
                    "pref": rec.get("pref", ""),
                    "city": rec.get("city", ""),
                    "town": rec.get("town", ""),
                    "custom": rec.get("custom", {}),
                }
            else:
                records[zc] = {"pref": "", "city": "", "town": "", "custom": {}}
        self._pending_zipcodes = selected
        self.custom_page.setup_records(records)
        self.stack.setCurrentWidget(self.custom_page)

    def _custom_page_accepted(self, data):
        reply = QMessageBox.question(
            self,
            "確認",
            f"{len(self._pending_zipcodes)} 件のレコードに適用しますか？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            msg = self.controller.update_custom_map(data)
            self.output.append(msg)
            self.perform_search(self.current_page)
        self.stack.setCurrentWidget(self.search_page)

    def _custom_page_cancelled(self):
        self.stack.setCurrentWidget(self.search_page)

    # --- log page related ---
    def load_logs_page(self, page: int = 1):
        logs, total = self.controller.fetch_logs(page, per_page=30)
        self.logs_page.logs = logs

        self.logs_page.details_model.removeRows(
            0, self.logs_page.details_model.rowCount()
        )

        self.logs_page.model.removeRows(0, self.logs_page.model.rowCount())
        for log in logs:
            type_item = QStandardItem("追加" if log["type"] == "add" else "削除")
            type_item.setData(log["index"], Qt.UserRole)
            file_item = QStandardItem(log.get("source_file", ""))
            count_item = QStandardItem(str(log.get("record_count", 0)))
            ts = log.get("timestamp", "")
            try:
                ts = __import__("datetime").datetime.fromisoformat(ts).strftime("%Y/%m/%d %H:%M")
            except Exception:
                pass
            ts_item = QStandardItem(ts)
            for item in [type_item, file_item, count_item, ts_item]:
                item.setEditable(False)
            self.logs_page.model.appendRow([type_item, file_item, count_item, ts_item])
        self.logs_page.table.clearSelection()

        self.log_current_page = page
        self.log_total_pages = max(1, (total + 29) // 30)
        self.logs_page.page_label.setText(f"{self.log_current_page} / {self.log_total_pages}")
        self.logs_page.prev_btn.setEnabled(self.log_current_page > 1)
        self.logs_page.next_btn.setEnabled(self.log_current_page < self.log_total_pages)

    def _selected_log_indices(self):
        indices = []
        for index in self.logs_page.table.selectionModel().selectedRows():
            item = self.logs_page.model.item(index.row(), 0)
            idx = item.data(Qt.UserRole)
            indices.append(idx)
        return indices

    def restore_selected_logs(self):
        indices = self._selected_log_indices()
        if not indices:
            return
        reply = QMessageBox.question(
            self,
            "確認",
            f"{len(indices)} 件の履歴を復元しますか？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            msg = self.controller.reverse_logs(indices)
            self.output.append(msg)
            self.load_logs_page(self.log_current_page)

    def delete_selected_logs(self):
        indices = self._selected_log_indices()
        if not indices:
            return
        reply = QMessageBox.question(
            self,
            "確認",
            f"{len(indices)} 件の履歴を削除しますか？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            msg = self.controller.delete_logs(indices)
            self.output.append(msg)
            self.load_logs_page(self.log_current_page)

    def reapply_selected_logs(self):
        indices = self._selected_log_indices()
        if not indices:
            return
        reply = QMessageBox.question(
            self,
            "確認",
            f"{len(indices)} 件の履歴を再実行しますか？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            msg = self.controller.reapply_logs(indices)
            self.output.append(msg)
            self.load_logs_page(self.log_current_page)

    # --- json import/export ---
    def import_json_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "JSONをインポート", "", "JSON Files (*.json)")
        if not path:
            return
        msg = self.controller.import_json(path)
        self.output.append(msg)

    def export_json_data(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "JSONをエクスポート", "address.json", "JSON Files (*.json)")
        if not path:
            return
        msg = self.controller.export_json(path)
        self.output.append(msg)
