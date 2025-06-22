from PySide6.QtWidgets import (
    QApplication,
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QFileDialog, QSizePolicy,
    QProgressDialog,
)
from PySide6.QtCore import Qt

from japanpost_backend.custom_builder import (
    load_data_strict,
    normalize_entries,
    normalize_course_codes,
    normalize_pickup_variants,
    build_customs,
    inject_customs,
    save_json,
)


class DeliverySettingPage(QWidget):
    """Page to import custom delivery settings from Excel."""

    def __init__(self, json_path: str):
        super().__init__()
        self.json_path = json_path

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
        try:
            address_dict, entries_df, courses_df, variants_df = load_data_strict(
                self.json_path, excel_path
            )
            entries = normalize_entries(entries_df)
            courses = normalize_course_codes(courses_df)
            variants = normalize_pickup_variants(variants_df)
            customs = build_customs(entries, courses, variants)
            inject_customs(address_dict, customs)
            save_json(self.json_path, address_dict)
            self.log("[OK] JSONを更新しました")
        except Exception as e:  # pragma: no cover - runtime errors shown to user
            self.log(f"[ERROR] {e}")
        finally:
            progress.close()
