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
        layout.setContentsMargins(16, 16, 16, 16)
        self.header_label = QLabel("カスタム項目追加")
        self.header_label.setObjectName("pageTitle")
        layout.addWidget(self.header_label)

        nav = QHBoxLayout()
        nav.setAlignment(Qt.AlignCenter)  # ① 中央に配置
        self.prev_btn = QPushButton("前へ")
        self.prev_btn.setObjectName("secondaryButton")
        self.next_btn = QPushButton("次へ")
        self.next_btn.setObjectName("secondaryButton")
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
        layout.addLayout(nav)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["キー", "値"])
        layout.addWidget(self.tree)

        # 操作用ボタン
        top_btns = QHBoxLayout()
        top_btns.setAlignment(Qt.AlignCenter)
        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("secondaryButton")
        self.remove_btn = QPushButton("－")
        self.remove_btn.setObjectName("dangerButton")
        self.add_child_btn = QPushButton("子要素を追加")
        self.add_child_btn.setObjectName("secondaryButton")
        for b in [self.add_btn, self.remove_btn, self.add_child_btn]:
            top_btns.addWidget(b)

        action_btns = QHBoxLayout()
        action_btns.setAlignment(Qt.AlignCenter)
        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.setObjectName("secondaryButton")
        self.ok_btn = QPushButton("決定")
        self.ok_btn.setObjectName("primaryButton")
        # ボタンサイズをそろえる
        max_w = max(self.cancel_btn.sizeHint().width(),
                    self.ok_btn.sizeHint().width())
        max_h = max(self.cancel_btn.sizeHint().height(),
                    self.ok_btn.sizeHint().height())
        self.cancel_btn.setFixedSize(max_w, max_h)
        self.ok_btn.setFixedSize(max_w, max_h)
        for b in [self.cancel_btn, self.ok_btn]:
            action_btns.addWidget(b)

        layout.addLayout(top_btns)
        layout.addSpacing(12)  # ② 1行開ける
        layout.addLayout(action_btns)

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
        """Move to the previous/next record and refresh view."""
        if not self._order:
            return
        self._save_current()
        self._index = max(0, min(len(self._order) - 1, self._index + step))
        self._load_current()
        self._update_nav()

    def _load_current(self):
        """Load current record info and populate the tree."""
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
        """Save the current tree state back to the record map."""
        if not self._order:
            return
        zc = self._order[self._index]
        self._records[zc] = self.get_data()

    def _update_nav(self):
        """Enable/disable navigation buttons."""
        self.prev_btn.setEnabled(self._index > 0)
        self.next_btn.setEnabled(self._index < len(self._order) - 1)

    def _populate_tree(self, data):
        """Populate tree widget from nested mapping."""
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
        """Add a new top level key/value pair."""
        item = QTreeWidgetItem(["key", "value"])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(item)

    def add_child_item(self):
        """Add a child node to the currently selected item."""
        current = self.tree.currentItem()
        if not current:
            return
        child = QTreeWidgetItem(["key", "value"])
        child.setFlags(child.flags() | Qt.ItemIsEditable)
        current.addChild(child)
        current.setExpanded(True)

    def remove_item(self):
        """Remove the selected item from the tree."""
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
        """Emit the accepted signal with current records."""
        self._save_current()
        self.accepted.emit(self._records)

    # --- data retrieval ---
    def get_data(self):
        """Return the current tree contents as a nested dict."""
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
        """Recursively build dictionary from QTreeWidgetItem."""
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

