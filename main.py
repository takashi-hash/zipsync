# アプリケーションのエントリーポイント

import sys
from PySide6.QtWidgets import QApplication
from ui_main import MainWindow

def main():
    """GUI を起動するメイン関数"""
    app = QApplication(sys.argv)
    with open("resources/styles/style.qss", encoding="utf-8") as f:
        app.setStyleSheet(app.styleSheet() + f.read())
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
