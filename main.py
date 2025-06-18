import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from ui_main import MainWindow

def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")  # ダーク・ティール系テーマを適用
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
