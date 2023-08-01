from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy


class VideoTab(QWidget):
    def __init__(self, frame, title):
        super().__init__()
        self.frame = frame
        self.title = title
        layout = QVBoxLayout()
        self.snapshot = QLabel()
        self.snapshot.setAlignment(Qt.AlignCenter)
        self.snapshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.snapshot)

        self.setLayout(layout)
