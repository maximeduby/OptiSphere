from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.progress = QProgressBar(objectName="progress-bar")
        self.progress.setTextVisible(False)
        self.status = QLabel(text="", objectName="status")
        self.percentage = QLabel(text="0%", objectName="legend")

        hl = QHBoxLayout()
        hl.setSpacing(10)
        hl.addWidget(self.progress)
        hl.addWidget(self.percentage)

        layout.addLayout(hl)
        layout.addWidget(self.status)
        self.setLayout(layout)

    @Slot()
    def update_progress(self, status, progress):
        self.progress.setValue(progress)
        self.percentage.setText(f"{progress}%")
        self.status.setText(status)

    def reset(self):
        self.progress.reset()
        self.percentage.setText("0%")
        self.status.setText("")
