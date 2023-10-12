import sys

from PySide6.QtWidgets import QApplication

from core.PathManager import get_path
from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication()
    app.setStyleSheet(open(get_path("resources/stylesheet.css")).read())
    window = MainWindow()
    sys.exit(app.exec())
