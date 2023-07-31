from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from configuration import ROOT_DIR


class CaptureButton(QPushButton):
    def __init__(self, parent_widget, title, icon_path):
        super().__init__()
        self.setIcon(QIcon(ROOT_DIR + "/resources/" + icon_path))
        self.clicked.connect(lambda: parent_widget.capture(self, title))
