from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QSizePolicy,
    QProgressDialog,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QFormLayout,
    QGroupBox,
    QStackedWidget,
    QMessageBox,
    QApplication,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
import json
from japanpost_backend import excel_custom_loader as loader_mod


class KeyListInput(QWidget):
    """Widget for editing a list of strings."""

    def __init__(self, initial=None, label="項目名"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(label))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("＋")
        self.add_btn.setObjectName("secondaryButton")
        self.del_btn = QPushButton("－")
        self.del_btn.setObjectName("dangerButton")
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.add_btn.clicked.connect(self.add_item)
        self.del_btn.clicked.connect(self.remove_selected)

        for item in initial or []:
            self.list_widget.addItem(item)

    def add_item(self):
        item = QListWidgetItem("")
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentItem(item)
        self.list_widget.editItem(item)

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_items(self):
        return [
            self.list_widget.item(i).text().strip()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).text().strip()
        ]


class DictArgsWidget(QWidget):
    def __init__(self, args):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.value_keys = KeyListInput(args.get("value_keys", []), label="value_keys")
        layout.addWidget(self.value_keys)

    def get_args(self):
        return {"value_keys": self.value_keys.get_items()}


class GroupedListArgsWidget(QWidget):
    def __init__(self, args):
        super().__init__()
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.group_key_edit = QLineEdit(args.get("group_value_key", ""))
        layout.addRow("group_value_key", self.group_key_edit)

    def get_args(self):
        return {"group_value_key": self.group_key_edit.text().strip()}


class DeepNestedArgsWidget(QWidget):
    def __init__(self, args):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.nest_keys = KeyListInput(args.get("nest_keys", []), label="nest_keys")
        layout.addWidget(self.nest_keys)
        self.value_map_edit = QTextEdit(
            json.dumps(args.get("value_map", {}), ensure_ascii=False, indent=2)
        )
        layout.addWidget(QLabel("value_map (JSON)"))
        layout.addWidget(self.value_map_edit)

    def get_args(self):
        try:
            value_map = json.loads(self.value_map_edit.toPlainText())
        except Exception:
            value_map = {}
        return {"nest_keys": self.nest_keys.get_items(), "value_map": value_map}


class LoaderConfigBlock(QGroupBox):
    removed = Signal(object)

    def __init__(self, config=None):
        super().__init__("シート設定")
        config = config or {}

        self.sheet_edit = QLineEdit(config.get("sheet", ""))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["dict", "grouped_list", "deep_nested_with_values"])
        self.method_combo.setCurrentText(config.get("method", "dict"))
        self.zip_edit = QLineEdit(config.get("args", {}).get("zip_key", "zipcode"))
        self.field_edit = QLineEdit(config.get("field_name") or "")
        self.remove_btn = QPushButton("削除")
        self.remove_btn.setObjectName("dangerButton")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        form_layout = QFormLayout()
        sheet_row_widget = QWidget()
        sheet_row = QHBoxLayout(sheet_row_widget)
        sheet_row.setContentsMargins(0, 0, 0, 0)
        sheet_row.addWidget(self.sheet_edit)
        sheet_row.addWidget(self.remove_btn)
        form_layout.addRow("シート名", sheet_row_widget)
        form_layout.addRow("処理方法", self.method_combo)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(QLabel("zip_key"))
        row_layout.addWidget(self.zip_edit)
        row_layout.addWidget(QLabel("field_name"))
        row_layout.addWidget(self.field_edit)
        form_layout.addRow(row_widget)

        layout.addLayout(form_layout)

        self.arg_stack = QStackedWidget()
        self.dict_args = DictArgsWidget(config.get("args", {}))
        self.grouped_args = GroupedListArgsWidget(config.get("args", {}))
        self.deep_args = DeepNestedArgsWidget(config.get("args", {}))
        self.arg_stack.addWidget(self.dict_args)
        self.arg_stack.addWidget(self.grouped_args)
        self.arg_stack.addWidget(self.deep_args)
        layout.addWidget(self.arg_stack)

        self.method_combo.currentTextChanged.connect(self.update_args_widget)
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))
        self.update_args_widget(self.method_combo.currentText())

    def update_args_widget(self, method):
        index = {"dict": 0, "grouped_list": 1, "deep_nested_with_values": 2}.get(method, 0)
        self.arg_stack.setCurrentIndex(index)

    def to_config(self):
        method = self.method_combo.currentText()
        args = {"zip_key": self.zip_edit.text().strip() or "zipcode"}
        args.update(self.arg_stack.currentWidget().get_args())
        return {
            "sheet": self.sheet_edit.text().strip(),
            "method": method,
            "args": args,
            "field_name": self.field_edit.text().strip() or None,
        }


class DeliverySettingPage(QWidget):
    def __init__(self, json_path):
        super().__init__()
        self.json_path = json_path
        self.blocks = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("配送設定")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        info = QLabel("Excelで管理する営業所コードなどをJSONに統合")
        info.setStyleSheet("color: gray")
        layout.addWidget(info)

        file_row = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setMinimumWidth(200)
        self.file_edit.setMaximumWidth(400)
        self.browse_btn = QPushButton("Excel選択")
        self.browse_btn.setObjectName("secondaryButton")
        self.browse_btn.setFixedHeight(40)
        self.browse_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.run_btn = QPushButton("実行")
        self.run_btn.setObjectName("primaryButton")
        self.run_btn.setFixedHeight(40)
        self.run_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_width = max(self.browse_btn.sizeHint().width(), self.run_btn.sizeHint().width())
        self.browse_btn.setFixedWidth(button_width)
        self.run_btn.setFixedWidth(button_width)
        file_row.addWidget(self.file_edit)
        file_row.addWidget(self.browse_btn)
        file_row.addWidget(self.run_btn)
        file_row.addStretch()
        layout.addLayout(file_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        self.block_layout = QHBoxLayout(scroll_content)
        self.block_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.add_btn = QPushButton("＋ シート設定追加")
        self.add_btn.setObjectName("secondaryButton")
        layout.addWidget(self.add_btn, alignment=Qt.AlignLeft)

        for cfg in self.default_config():
            self.add_config_block(cfg)

        self.browse_btn.clicked.connect(self.choose_file)
        self.run_btn.clicked.connect(self.run_process)
        self.add_btn.clicked.connect(lambda: self.add_config_block())

    def default_config(self):
        return [
            {
                "sheet": "entries",
                "method": "dict",
                "args": {
                    "zip_key": "zipcode",
                    "value_keys": [
                        "office_code",
                        "destination_name",
                        "shiwake_code",
                    ],
                },
            },
            {
                "sheet": "course_codes",
                "method": "grouped_list",
                "args": {"zip_key": "zipcode", "group_value_key": "course_code"},
                "field_name": "course_codes",
            },
            {
                "sheet": "pickup_variants",
                "method": "deep_nested_with_values",
                "args": {
                    "zip_key": "zipcode",
                    "nest_keys": ["pickup_location", "delivery_type"],
                    "value_map": {
                        "pickup_location": ["destination_name"],
                        "delivery_type": ["shiwake_code"],
                    },
                },
                "field_name": "pickup_variants",
            },
        ]

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Excelファイルを選択", "", "Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.file_edit.setText(path)

    def add_config_block(self, cfg=None):
        block = LoaderConfigBlock(cfg)
        block.removed.connect(self.remove_config_block)
        self.blocks.append(block)
        self.block_layout.addWidget(block)

    def remove_config_block(self, block):
        if block in self.blocks:
            self.blocks.remove(block)
        self.block_layout.removeWidget(block)
        block.deleteLater()

    def run_process(self):
        excel_path = self.file_edit.text().strip()
        if not excel_path:
            QMessageBox.warning(self, "エラー", "Excelファイルを指定してください")
            return

        progress = QProgressDialog("処理中...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        QApplication.processEvents()

        try:
            loaders = [
                loader_mod.create_loader(
                    path=excel_path,
                    sheet=b.to_config()["sheet"],
                    method=b.to_config()["method"],
                    args=b.to_config()["args"],
                    field_name=b.to_config()["field_name"],
                )
                for b in self.blocks
            ]
            loader_mod.update_address_json(
                json_path=self.json_path,
                excel_path=excel_path,
                loaders=loaders,
                output_path=self.json_path,
            )
            QMessageBox.information(self, "成功", "JSONを更新しました")
        except Exception as e:  # pragma: no cover - runtime errors shown to user
            QMessageBox.critical(self, "エラー", str(e))
        finally:
            progress.close()
