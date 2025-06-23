from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QSizePolicy,
    QProgressDialog,
    QComboBox,
    QFormLayout,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal
import json
from japanpost_backend import excel_custom_loader as loader_mod


class LoaderConfigBlock(QGroupBox):
    """Widget representing a single loader configuration block."""

    removed = Signal(object)

    def __init__(self, config: dict | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        if config is None:
            config = {}

        self.setTitle("シート設定")
        self.form = QFormLayout(self)

        self.sheet_edit = QLineEdit(config.get("sheet", ""))
        self.form.addRow("シート名", self.sheet_edit)

        self.method_combo = QComboBox()
        self.method_combo.addItems(["dict", "grouped_list", "deep_nested_with_values"])
        m = config.get("method", "dict")
        if m in ["dict", "grouped_list", "deep_nested_with_values"]:
            self.method_combo.setCurrentText(m)
        self.form.addRow("処理方法", self.method_combo)

        self.zip_edit = QLineEdit(config.get("args", {}).get("zip_key", "zipcode"))
        self.form.addRow("zip_key", self.zip_edit)

        self.field_edit = QLineEdit(config.get("field_name") or "")
        self.form.addRow("field_name", self.field_edit)

        self.args_widget = QWidget()
        self.args_layout = QFormLayout(self.args_widget)
        self.form.addRow(self.args_widget)

        self.remove_btn = QPushButton("削除")
        self.remove_btn.setObjectName("dangerButton")
        self.form.addRow(self.remove_btn)

        self.method_combo.currentTextChanged.connect(self._refresh_args)
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))

        self._refresh_args(config.get("args", {}))

    # --- internal ---
    def _refresh_args(self, args: dict | None = None) -> None:
        if args is None:
            args = {}
        while self.args_layout.rowCount() > 0:
            self.args_layout.removeRow(0)

        method = self.method_combo.currentText()
        if method == "dict":
            self.value_keys_edit = QLineEdit(",".join(args.get("value_keys", [])))
            self.args_layout.addRow("value_keys(,区切り)", self.value_keys_edit)
        elif method == "grouped_list":
            self.group_value_key_edit = QLineEdit(args.get("group_value_key", ""))
            self.args_layout.addRow("group_value_key", self.group_value_key_edit)
        elif method == "deep_nested_with_values":
            self.nest_keys_edit = QLineEdit(",".join(args.get("nest_keys", [])))
            self.value_map_edit = QTextEdit(
                json.dumps(args.get("value_map", {}), ensure_ascii=False, indent=2)
            )
            self.args_layout.addRow("nest_keys(,区切り)", self.nest_keys_edit)
            self.args_layout.addRow("value_map(JSON)", self.value_map_edit)

    # --- public ---
    def to_config(self) -> dict:
        method = self.method_combo.currentText()
        args: dict = {"zip_key": self.zip_edit.text().strip() or "zipcode"}
        if method == "dict":
            keys = self.value_keys_edit.text().strip()
            args["value_keys"] = [k.strip() for k in keys.split(",") if k.strip()]
        elif method == "grouped_list":
            args["group_value_key"] = self.group_value_key_edit.text().strip()
        elif method == "deep_nested_with_values":
            nest = [k.strip() for k in self.nest_keys_edit.text().split(",") if k.strip()]
            args["nest_keys"] = nest
            try:
                val = json.loads(self.value_map_edit.toPlainText() or "{}")
            except Exception:
                val = {}
            args["value_map"] = val
        return {
            "sheet": self.sheet_edit.text().strip(),
            "method": method,
            "args": args,
            "field_name": self.field_edit.text().strip() or None,
        }

class DeliverySettingPage(QWidget):
    """Page to import custom delivery settings from Excel."""

    def __init__(self, json_path: str):
        super().__init__()
        self.json_path = json_path
        self.blocks: list[LoaderConfigBlock] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("配送設定")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        info = QLabel(
            "Excel で管理する営業所コードやコースコードなどの配送設定を、\n"
            "住所データに統合します。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: gray;")
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
        button_width = max(
            self.browse_btn.sizeHint().width(),
            self.run_btn.sizeHint().width(),
        )
        self.browse_btn.setFixedWidth(button_width)
        self.run_btn.setFixedWidth(button_width)
        file_row.addWidget(self.file_edit)
        file_row.addWidget(self.browse_btn)
        file_row.addWidget(self.run_btn)
        layout.addLayout(file_row)

        self.block_area = QVBoxLayout()
        layout.addLayout(self.block_area)

        self.add_block_btn = QPushButton("＋ シート設定追加")
        self.add_block_btn.setObjectName("secondaryButton")
        self.add_block_btn.clicked.connect(lambda: self.add_config_block())
        layout.addWidget(self.add_block_btn, alignment=Qt.AlignLeft)

        # --- initial template ---
        default_cfg = [
            {
                "sheet": "entries",
                "method": "dict",
                "args": {
                    "zip_key": "zipcode",
                    "value_keys": ["office_code", "destination_name", "shiwake_code"],
                },
                "field_name": None,
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
        for cfg in default_cfg:
            self.add_config_block(cfg)

        layout.addStretch()

        self.browse_btn.clicked.connect(self.choose_file)
        self.run_btn.clicked.connect(self.run_process)

    # --- helpers ---
    def log(self, text: str) -> None:
        print(text)

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Excelファイルを選択", "", "Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.file_edit.setText(path)

    def run_process(self) -> None:
        excel_path = self.file_edit.text().strip()
        if not excel_path:
            self.log("[ERROR] Excelファイルを指定してください")
            return
        progress = QProgressDialog("処理中...", None, 0, 0, self)
        progress.setWindowTitle("Please wait")
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setRange(0, 0)
        progress.show()
        QApplication.processEvents()
        loaders = []
        for cfg in [b.to_config() for b in self.blocks]:
            try:
                loaders.append(
                    loader_mod.create_loader(
                        path=excel_path,
                        sheet=cfg.get("sheet", ""),
                        method=cfg.get("method", ""),
                        args=cfg.get("args", {}),
                        field_name=cfg.get("field_name"),
                    )
                )
            except Exception as e:
                self.log(f"[ERROR] loader設定エラー: {e}")
                progress.close()
                return

        try:
            loader_mod.update_address_json(
                json_path=self.json_path,
                excel_path=excel_path,
                loaders=loaders,
                output_path=self.json_path,
            )
            self.log("[OK] JSONを更新しました")
        except Exception as e:  # pragma: no cover - runtime errors shown to user
            self.log(f"[ERROR] {e}")
        finally:
            progress.close()

    # --- block helpers ---
    def add_config_block(self, cfg: dict | None = None) -> None:
        block = LoaderConfigBlock(cfg)
        block.removed.connect(self.remove_config_block)
        self.blocks.append(block)
        self.block_area.addWidget(block)

    def remove_config_block(self, block: LoaderConfigBlock) -> None:
        if block in self.blocks:
            self.blocks.remove(block)
        self.block_area.removeWidget(block)
        block.deleteLater()
