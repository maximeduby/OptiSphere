from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QSpinBox, QDialog, QDialogButtonBox, QPushButton, QHBoxLayout

from ui.widgets.HMSTimeWidget import HMSTimeWidget


class EditTimelapseDialog(QDialog):
    def __init__(self, duration, delta_time):
        super().__init__()
        self.setWindowTitle("Edit Timelapse Settings")

        self.prev_duration = duration
        self.prev_delta_time = delta_time

        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.duration = HMSTimeWidget(self.prev_duration)
        self.delta_time = QSpinBox()
        self.delta_time.setMinimum(0)
        self.delta_time.setValue(self.prev_delta_time)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(text="Start", objectName="accept-btn")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(text="Cancel", objectName="reject-btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("Recording Duration:", self.duration)
        layout.addRow("Delta Time (seconds):", self.delta_time)
        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_duration(self):
        return self.duration.get_value()

    def get_delta_time(self):
        return self.delta_time.value()