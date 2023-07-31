import cv2
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SnapshotTab(QWidget):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        layout = QVBoxLayout()
        self.snapshot = QLabel()
        layout.addWidget(self.snapshot)

        self.setLayout(layout)

    @Slot()
    def set_image(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        image = image.scaled(self.snapshot.size() * 0.99, Qt.KeepAspectRatio)
        self.snapshot.setPixmap(QPixmap.fromImage(image))