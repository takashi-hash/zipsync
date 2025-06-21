# アプリケーションのエントリーポイント

import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from ui_main import MainWindow

def main():
    """GUI を起動するメイン関数"""
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="light_blue.xml")
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
