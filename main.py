import sys

from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import QApplication

from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()

    # detect when new Camera is plugged or unplugged
    device = QMediaDevices()
    device.videoInputsChanged.connect(window.update_cameras)

    sys.exit(app.exec())
