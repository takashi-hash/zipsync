# アプリケーションのエントリーポイント

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from qt_material import apply_stylesheet
from ui_main import MainWindow

def main():
    """GUI を起動するメイン関数"""
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont("resources/fonts/Inter-Regular.ttf")
    app.setFont(QFont("Inter", 14))
    apply_stylesheet(app, theme="resources/themes/easy_reading.xml")
    with open("resources/styles/style.qss") as f:
        app.setStyleSheet(app.styleSheet() + f.read())
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
