import sys

from PySide6.QtWidgets import QApplication

from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(open("stylesheet.css").read())
    window = MainWindow()
    sys.exit(app.exec())
