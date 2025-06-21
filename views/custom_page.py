# カスタムデータを入力するページ

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal


class CustomEditPage(QWidget):
    """ネストしたカスタムデータを入力するページ"""
    """Page to input nested custom data."""

    accepted = Signal(dict)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.header_label = QLabel("カスタム項目追加")
        layout.addWidget(self.header_label)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("前へ")
        self.next_btn = QPushButton("次へ")
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        self.index_label = QLabel("")
        self.zip_label = QLabel("")
        self.pref_label = QLabel("")
        self.city_label = QLabel("")
        self.town_label = QLabel("")
        for w in [self.index_label, self.zip_label, self.pref_label,
                  self.city_label, self.town_label]:
            info_layout.addWidget(w)
        nav.addWidget(self.prev_btn)
        nav.addWidget(info_widget)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        layout.addLayout(nav)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["キー", "値"])
        layout.addWidget(self.tree)

        btns = QHBoxLayout()
        btns.setAlignment(Qt.AlignCenter)
        self.add_btn = QPushButton("＋")
        self.remove_btn = QPushButton("－")
        self.add_child_btn = QPushButton("子要素を追加")
        self.cancel_btn = QPushButton("キャンセル")
        self.ok_btn = QPushButton("決定")
        for b in [self.add_btn, self.remove_btn, self.add_child_btn,
                  self.cancel_btn, self.ok_btn]:
            btns.addWidget(b)
        layout.addLayout(btns)

        # unify button widths
        width = max(b.sizeHint().width() for b in [self.add_btn, self.remove_btn,
                                                   self.add_child_btn,
                                                   self.cancel_btn, self.ok_btn])
        for b in [self.add_btn, self.remove_btn, self.add_child_btn,
                  self.cancel_btn, self.ok_btn]:
            b.setFixedWidth(width)

        self.add_btn.clicked.connect(self.add_root_item)
        self.add_child_btn.clicked.connect(self.add_child_item)
        self.remove_btn.clicked.connect(self.remove_item)
        self.ok_btn.clicked.connect(self._emit_accept)
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        self.prev_btn.clicked.connect(lambda: self._navigate(-1))
        self.next_btn.clicked.connect(lambda: self._navigate(1))

        self._records = {}
        self._info = {}
        self._order = []
        self._index = 0

    # --- navigation helpers ---
    def _navigate(self, step: int):
        if not self._order:
            return
        self._save_current()
        self._index = max(0, min(len(self._order) - 1, self._index + step))
        self._load_current()
        self._update_nav()

    def _load_current(self):
        self.tree.clear()
        if not self._order:
            for lbl in [self.index_label, self.zip_label, self.pref_label,
                        self.city_label, self.town_label]:
                lbl.setText("")
            return
        zc = self._order[self._index]
        info = self._info.get(zc, {})
        data = self._records.get(zc, {})
        self.index_label.setText(
            f"現在表示中({self._index + 1}/{len(self._order)})")
        self.zip_label.setText(f"郵便番号: {zc}")
        self.pref_label.setText(f"都道府県: {info.get('pref', '')}")
        self.city_label.setText(f"市区町村: {info.get('city', '')}")
        self.town_label.setText(f"町域: {info.get('town', '')}")
        self._populate_tree(data)

    def _save_current(self):
        if not self._order:
            return
        zc = self._order[self._index]
        self._records[zc] = self.get_data()

    def _update_nav(self):
        self.prev_btn.setEnabled(self._index > 0)
        self.next_btn.setEnabled(self._index < len(self._order) - 1)

    def _populate_tree(self, data):
        def add_items(parent, d):
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, list):
                        for item in v:
                            child = QTreeWidgetItem([k, ""])
                            child.setFlags(child.flags() | Qt.ItemIsEditable)
                            add_items(child, item)
                            parent.addChild(child)
                    else:
                        child = QTreeWidgetItem([k, ""] if isinstance(v, dict) else [k, str(v)])
                        child.setFlags(child.flags() | Qt.ItemIsEditable)
                        if isinstance(v, dict):
                            add_items(child, v)
                        parent.addChild(child)
            else:
                # not expected
                pass

        for k, v in (data or {}).items():
            item = QTreeWidgetItem([k, ""] if isinstance(v, dict) else [k, str(v)])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            if isinstance(v, dict):
                add_items(item, v)
            self.tree.addTopLevelItem(item)

    # --- public API ---
    def setup_records(self, records: dict):
        """Initialize page with mapping
        {zipcode: {pref:str, city:str, town:str, custom:dict}}."""
        self._info = {}
        self._records = {}
        for zc, rec in records.items():
            self._info[zc] = {
                "pref": rec.get("pref", ""),
                "city": rec.get("city", ""),
                "town": rec.get("town", ""),
            }
            self._records[zc] = rec.get("custom", {})
        self._order = list(records.keys())
        self._index = 0
        self._load_current()
        self._update_nav()

    # --- button handlers ---
    def add_root_item(self):
        item = QTreeWidgetItem(["key", "value"])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(item)

    def add_child_item(self):
        current = self.tree.currentItem()
        if not current:
            return
        child = QTreeWidgetItem(["key", "value"])
        child.setFlags(child.flags() | Qt.ItemIsEditable)
        current.addChild(child)
        current.setExpanded(True)

    def remove_item(self):
        current = self.tree.currentItem()
        if not current:
            return
        parent = current.parent()
        if parent:
            parent.removeChild(current)
        else:
            idx = self.tree.indexOfTopLevelItem(current)
            if idx >= 0:
                self.tree.takeTopLevelItem(idx)

    def _emit_accept(self):
        self._save_current()
        self.accepted.emit(self._records)

    # --- data retrieval ---
    def get_data(self):
        result = {}
        for i in range(self.tree.topLevelItemCount()):
            key, val = self._build_dict(self.tree.topLevelItem(i))
            if key in result:
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(val)
            else:
                result[key] = val
        return result

    def _build_dict(self, item):
        if item.childCount() > 0:
            d = {}
            for i in range(item.childCount()):
                k, v = self._build_dict(item.child(i))
                if k in d:
                    if not isinstance(d[k], list):
                        d[k] = [d[k]]
                    d[k].append(v)
                else:
                    d[k] = v
            return item.text(0), d
        else:
            return item.text(0), item.text(1)

