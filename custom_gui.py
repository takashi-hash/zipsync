import os
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QProgressDialog,
)
from PySide6.QtCore import Qt

from custom_builder import (
    load_data_strict,
    normalize_entries,
    normalize_course_codes,
    normalize_pickup_variants,
    build_customs,
    inject_customs,
    save_json,
)


class CustomInsertApp(QWidget):
    """Simple GUI to insert custom data into address JSON."""

    def __init__(self, json_path: str):
        super().__init__()
        self.json_path = json_path
        self.setWindowTitle("Custom JSON Builder")

        layout = QVBoxLayout(self)

        file_row = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setMinimumWidth(200)
        self.file_button = QPushButton("Excel選択")
        self.run_button = QPushButton("実行")
        # unify button width
        button_width = max(
            self.file_button.sizeHint().width(),
            self.run_button.sizeHint().width(),
        )
        self.file_button.setFixedWidth(button_width)
        self.run_button.setFixedWidth(button_width)
        file_row.addWidget(QLabel("Excelファイル:"))
        file_row.addWidget(self.file_edit, 1)
        file_row.addWidget(self.file_button)
        file_row.addWidget(self.run_button)
        layout.addLayout(file_row)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.file_button.clicked.connect(self.choose_file)
        self.run_button.clicked.connect(self.run_process)

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


def main() -> None:
    json_path = os.path.join(os.getcwd(), "data", "address.json")
    app = QApplication(sys.argv)
    window = CustomInsertApp(json_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
