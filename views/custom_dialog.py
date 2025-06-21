# ネストしたカスタムデータ入力ダイアログ

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel
)
from PySide6.QtCore import Qt


class CustomEditDialog(QDialog):
    """ネストしたカスタムデータを入力するダイアログ"""
    """Dialog to input nested custom data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("カスタム項目追加")
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["キー", "値"])
        layout.addWidget(self.tree)

        btns = QHBoxLayout()
        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("secondaryButton")
        self.add_child_btn = QPushButton("＋子")
        self.add_child_btn.setObjectName("secondaryButton")
        self.remove_btn = QPushButton("－")
        self.remove_btn.setObjectName("dangerButton")
        btns.addWidget(self.add_btn)
        btns.addWidget(self.add_child_btn)
        btns.addWidget(self.remove_btn)
        btns.addStretch()
        layout.addLayout(btns)

        action = QHBoxLayout()
        self.ok_btn = QPushButton("決定")
        self.ok_btn.setObjectName("primaryButton")
        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.setObjectName("secondaryButton")
        action.addWidget(self.ok_btn)
        action.addWidget(self.cancel_btn)
        action.addStretch()
        layout.addLayout(action)

        self.add_btn.clicked.connect(self.add_root_item)
        self.add_child_btn.clicked.connect(self.add_child_item)
        self.remove_btn.clicked.connect(self.remove_item)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

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

