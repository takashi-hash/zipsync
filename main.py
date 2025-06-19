import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from ui_main import MainWindow

def main():
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="resources/themes/easy_reading.xml")
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
